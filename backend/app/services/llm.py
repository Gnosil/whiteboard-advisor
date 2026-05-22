"""千帆 LLM 编排层。

- 真实模式:调用千帆 v2 (OpenAI 兼容, Bearer 鉴权),要求 JSON 输出
- Mock 模式:无 key 时用规则生成可用的 TurnPlan,保证全流程可跑通
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from enum import Enum
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import ActionType, IntentType, Language, Session, TurnPlan
from app.services import cost, rag
from app.templates import registry

logger = logging.getLogger("whiteboard-advisor.llm")


class TaskKind(str, Enum):
    turn = "turn"          # 交互轮:意图+zone+解说,用快模型
    deep_plan = "deep_plan"  # 复杂多 zone 规划,用 deep 模型


def _model_for(kind: TaskKind) -> str:
    return settings.model_deep if kind == TaskKind.deep_plan else settings.model_fast


# 简单内存 turn 缓存:相同 (模板 + zone 状态 + 用户话) 24h 内复用,省成本/延迟
_CACHE_TTL = 24 * 3600
_turn_cache: dict[str, tuple[float, str]] = {}


def _cache_key(session: Session, utterance: str) -> str:
    zones_state = {zid: z.data for zid, z in session.zones.items() if z.data}
    raw = json.dumps(
        {"t": session.template_id, "z": zones_state, "u": utterance},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_get(key: str) -> Optional[str]:
    hit = _turn_cache.get(key)
    if not hit:
        return None
    ts, content = hit
    if time.time() - ts > _CACHE_TTL:
        _turn_cache.pop(key, None)
        return None
    return content


def _cache_put(key: str, content: str) -> None:
    if len(_turn_cache) > 500:
        _turn_cache.clear()
    _turn_cache[key] = (time.time(), content)

SYSTEM_PROMPT = """你是一位资深的保险与财富规划顾问,正在通过"实时画白板"的方式帮客户做开局规划演示。

你的工作:根据客户的口语输入,在 family-protection 模板的若干 zone 上填充或修改**结构化数据**(不是 HTML)。

可用 zone 及其数据 JSON Schema:
{zone_schemas}

每一轮你必须输出**严格的 JSON**,字段如下:
{{
  "intent": 六选一: "provide_info" | "modify_request" | "clarification_question" | "topic_switch" | "out_of_scope" | "terminate",
  "action": "update_zone" | "modify_zone" | "explain" | "switch_focus" | "ask_next" | "finalize",
  "target_zone": zone 的 id,或 null,
  "zone_data": 当 action 为 update_zone/modify_zone 时,给出 target_zone 的**完整新 data**(必须匹配该 zone 的 schema);否则为 null,
  "narration": 你要用语音对客户说的话(口语、自然、简短,2-4 句),
  "next_question": 你想主动追问客户的下一个问题,或 null
}}

★ narration 的核心要求(这是产品最关键的体验):
narration 不是泛泛的回应,而是**向客户解说你刚刚在白板上做了哪些改动、以及为什么这么分析**。
- update_zone:说清你在「哪个模块」新画/填了「什么内容」。例:"我在保障缺口这块画上了:你目前寿险是空白,按你 300 万资产和三个孩子,建议额度大概 300 万美金,所以这里有一个明显缺口。"
- modify_zone:对比改动前后,说清你把「什么」从「旧值」改成了「新值」,以及原因。例:"我把寿险保额从 300 万上调到了 500 万,因为你刚提到还要覆盖两个孩子的海外学费。"
- explain:不改白板时,指向对应模块解释客户的疑问。
让客户听着 narration,就能明白屏幕上刚刚长出来/变化的那部分是什么、为什么。

规则:
- 客户提供新信息时,把它整理进最相关的 zone,zone_data 给出该 zone 合并后的完整 data;narration 必须解说这次改动。
- 你能在上下文里看到该 zone 改动前的 data(zones_so_far),做 modify 时请据此对比出"改了什么"再说出来。
- 客户没说够时,礼貌追问(next_question),不要瞎编客户的资产数字。
- 始终用"一般性思路 (general guidance)"措辞,不给具体股票/基金代码,不预测市场涨跌。
- 涉及具体产品配置时,在 coverage_plan 的 disclaimer 里写明"具体产品请咨询持牌经纪人"。
- 语言:用 {language} 与客户交流(narration / next_question / 文案均用该语言)。
- 只输出 JSON,不要任何额外文字或 markdown 代码块。"""


def _infer_jurisdiction(session: Session, utterance: str) -> str:
    text = utterance + " ".join(e.content for e in session.dialogue_history[-6:])
    if any(k in text for k in ["香港", "HK", "港", "粤"]):
        return "HK"
    if any(k in text for k in ["美国", "US", "美籍", "纽约", "加州"]):
        return "US"
    return "global"


def _zone_schemas_text(template_id: str) -> str:
    parts = []
    for z in registry.template_zone_defs(template_id):
        parts.append(f"- {z['id']} ({z['title']['zh']}):\n{json.dumps(z['schema'], ensure_ascii=False)}")
    return "\n".join(parts)


def _build_messages(session: Session, utterance: str, repair_hint: Optional[str] = None) -> list[dict]:
    lang = "中文" if session.language == Language.zh else "English"
    system = SYSTEM_PROMPT.format(zone_schemas=_zone_schemas_text(session.template_id), language=lang)

    zones_state = {zid: z.data for zid, z in session.zones.items() if z.data}
    context = {
        "current_zone_focus": session.current_zone_focus,
        "zones_so_far": zones_state,
        "recent_dialogue": [
            {"role": e.role, "content": e.content} for e in session.dialogue_history[-8:]
        ],
    }
    jurisdiction = _infer_jurisdiction(session, utterance)
    kb = rag.context_block(utterance, jurisdiction)
    kb_section = f"\n\n{kb}\n" if kb else ""

    user_content = (
        f"当前白板状态:\n{json.dumps(context, ensure_ascii=False)}\n\n"
        f"客户最新说的话:「{utterance}」{kb_section}\n请输出本轮的 JSON。"
    )
    if repair_hint:
        user_content += f"\n\n注意:上一次输出的 zone_data 未通过 schema 校验,错误:{repair_hint}。请修正后重新输出完整 JSON。"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]


async def _call_qianfan(messages: list[dict], model: str) -> tuple[str, dict]:
    url = f"{settings.qianfan_base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {settings.qianfan_api_key}"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }
    # deepseek 等推理型模型较慢,且上下文增长后更慢,给足读超时
    timeout = httpx.Timeout(connect=10, read=120, write=30, pool=10)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"], data.get("usage", {})


def _parse_turn(raw: str) -> TurnPlan:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
    obj = json.loads(text)
    return TurnPlan.model_validate(obj)


async def generate_turn(
    session: Session,
    utterance: str,
    repair_hint: Optional[str] = None,
    kind: TaskKind = TaskKind.turn,
) -> TurnPlan:
    if not settings.has_llm:
        return _mock_turn(session, utterance)
    cost.check_budget(session.llm_cost)

    cache_key = _cache_key(session, utterance) if repair_hint is None else None
    if cache_key:
        cached = _cache_get(cache_key)
        if cached:
            return _parse_turn(cached)

    messages = _build_messages(session, utterance, repair_hint)
    model = _model_for(kind)
    try:
        raw, usage = await _call_qianfan(messages, model)
    except httpx.HTTPStatusError as e:
        # 快模型不可用(如未开通)时回退到 deep 模型
        if kind == TaskKind.turn and model != settings.model_deep:
            logger.warning("快模型 %s 调用失败(%s),回退 deep 模型", model, e.response.status_code)
            model = settings.model_deep
            raw, usage = await _call_qianfan(messages, model)
        else:
            raise
    session.llm_cost += cost.estimate(
        model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
    )
    if cache_key:
        _cache_put(cache_key, raw)
    return _parse_turn(raw)


# ---- Mock 模式:无 key 时跑通流程 ----

def _mock_turn(session: Session, utterance: str) -> TurnPlan:
    zone_ids = registry.template_zone_ids(session.template_id)
    filled = [z for z in zone_ids if session.zones.get(z) and session.zones[z].data]
    next_zone = next((z for z in zone_ids if z not in filled), None)

    if next_zone == "family_profile" or (next_zone is None and not filled):
        return TurnPlan(
            intent=IntentType.provide_info,
            action=ActionType.update_zone,
            target_zone="family_profile",
            zone_data={
                "members": [
                    {"role": "本人", "age": 52, "location": "香港"},
                    {"role": "子女", "location": "多伦多"},
                    {"role": "子女", "location": "伦敦"},
                    {"role": "子女", "location": "上海"},
                ],
                "summary": "(mock) 三孩跨三地,需考虑跨境保障与传承。",
            },
            narration="(mock 模式) 我先帮你把家庭结构画出来:你和三个分别在多伦多、伦敦、上海的孩子。",
            next_question="你目前手头大概有多少可投资资产?",
        )
    if next_zone == "protection_gap":
        return TurnPlan(
            intent=IntentType.provide_info,
            action=ActionType.update_zone,
            target_zone="protection_gap",
            zone_data={
                "items": [
                    {"category": "寿险", "current": 0, "recommended": 3000000, "gap": 3000000, "unit": "USD"},
                    {"category": "重疾", "current": 0, "recommended": 1000000, "gap": 1000000, "unit": "USD"},
                ],
                "summary": "(mock) 寿险与重疾保障基本为空白,是首要缺口。",
            },
            narration="(mock 模式) 看保障缺口,你目前寿险和重疾几乎是空白,这是最该补的两块。",
            next_question="想优先解决哪一块?",
        )
    if next_zone == "coverage_plan":
        return TurnPlan(
            intent=IntentType.provide_info,
            action=ActionType.update_zone,
            target_zone="coverage_plan",
            zone_data={
                "products": [
                    {"type": "定期寿险", "coverage": 3000000, "term": "20年", "rationale": "覆盖跨境家庭的收入替代缺口。", "unit": "USD"},
                    {"type": "重疾险", "coverage": 1000000, "term": "终身", "rationale": "应对重疾医疗与收入中断。", "unit": "USD"},
                ],
                "disclaimer": "这是一般性思路,具体产品请咨询持牌经纪人。",
            },
            narration="(mock 模式) 配置上,我建议一份定期寿险打底,加一份终身重疾。这只是方向,落地要找持牌经纪人。",
            next_question="要不要让一位专业经纪人帮你深入做一版?",
        )
    if next_zone is not None:
        # 非 family 模板的 zone:mock 下仅追问,不杜撰数据
        title = registry.zl.ALL_ZONE_BY_ID.get(next_zone, {}).get("title", {}).get("zh", next_zone)
        return TurnPlan(
            intent=IntentType.clarification_question,
            action=ActionType.ask_next,
            target_zone=next_zone,
            narration=f"(mock 模式) 接下来看「{title}」,需要你补充一些信息。",
            next_question=f"关于{title},能跟我说说你的情况吗?",
        )
    return TurnPlan(
        intent=IntentType.terminate,
        action=ActionType.finalize,
        target_zone=None,
        narration="(mock 模式) 我们已经过了一遍各个模块。",
        next_question=None,
    )
