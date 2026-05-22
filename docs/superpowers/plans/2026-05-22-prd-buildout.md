# WhiteboardAdvisor PRD 全量建设 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 PRD v0.1 里 V0.1 闭环之外、所有"花费时间的工程项"逐项做完——补齐 9 个 zone 与多模板、降低延迟、对话健壮性、Session 增强、LLM 编排完善、RAG 知识库、Broker Lead Funnel、Onboarding/persona——凡是纯软件能实现的全部落地;依赖外部资源(真实 broker、全量爬虫、应用商店、云账号、Stripe)的部分,用 mock/种子数据把软件闭环跑通并标注剩余外部对接。

**Architecture:** 现有 FastAPI(WebSocket)+ React/Vite/TS 单仓。后端按服务拆分(dialogue/zone_engine/llm/speech/session_store + 新增 rag/broker/cost)。模板与 zone schema 数据驱动,LLM 只产出结构化 JSON,前端纯函数渲染。新增 pytest 测试基建,核心逻辑 TDD。

**Tech Stack:** Python 3.9 / FastAPI / pydantic v2 / jsonschema / httpx / pytest;React 18 / Vite / TypeScript / framer-motion;千帆(LLM,OpenAI 兼容)+ 百度语音(ASR/TTS);RAG 用内存向量检索(种子库)可选 Qdrant;PDF 用 reportlab。

## 范围边界(已决策)
- **全部用纯软件实现**:9 zone、4 模板、模型分流、依赖管理、健壮性、PDF/分享、cost/cache/guardrails、RAG 检索服务+种子库、Broker funnel 软件闭环+mock broker、onboarding/persona/i18n。
- **标注外部对接、不在本计划内**:真实 carrier 全量爬虫(只做可运行小样例+种子)、真实 broker 网络、React Native 移植、AWS/Qdrant Cloud 部署、Stripe 真实计费(只做 Premium 占位与 gating)。
- 不做大陆合规、不做账户连接(Plaid)。

---

## Phase 0: 测试基建

### Task 0.1: 引入 pytest + FakeLLM

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/fakes.py`

- [ ] Step 1: `requirements.txt` 增加 `pytest==8.3.4` `pytest-asyncio==0.24.0`
- [ ] Step 2: `pytest.ini` 配置 `asyncio_mode=auto`、`testpaths=tests`、`pythonpath=.`
- [ ] Step 3: `tests/fakes.py` 写 `FakeLLM`:可预置一串 `TurnPlan` 按顺序返回,记录收到的 prompt;用于替换 `llm.generate_turn`
- [ ] Step 4: `conftest.py` 提供 `fresh_session` fixture(已 init_zones 的 Session)
- [ ] Step 5: 运行 `pip install -r requirements.txt && pytest -q`,Expected: collected 0 items(无测试也成功)
- [ ] Step 6: Commit `test: 引入 pytest + FakeLLM 基建`

### Task 0.2: 锁定现有逻辑的回归测试

**Files:**
- Create: `backend/tests/test_zone_engine.py`
- Create: `backend/tests/test_dialogue.py`

- [ ] Step 1: `test_zone_engine.py`:合法 family_profile data → `validate_zone_data` 返回 None;缺 `members` → 返回非空错误串;`apply_patch` 后 version+1、state=filled;非法 data 抛 `ZoneValidationError`
- [ ] Step 2: `test_dialogue.py`(用 FakeLLM monkeypatch `llm.generate_turn`):provide_info 轮 → 产出 zone_update + ai_message;校验失败两次 → 第三次降级为 explain(无 zone_update);terminate → finalize 事件
- [ ] Step 3: 运行 `pytest -q`,Expected: all pass
- [ ] Step 4: Commit `test: zone_engine 与 dialogue 回归测试`

---

## Phase 1: 延迟优化(模型分流)

**动机:** deepseek-v4-pro 单轮 18-47s,体感差。按任务分流到快/慢模型。

### Task 1.1: 多模型配置 + 任务级分流

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/services/llm.py`
- Modify: `backend/.env.example`
- Create: `backend/tests/test_llm_routing.py`

- [ ] Step 1: `config.py` 增 `qianfan_model_fast`(默认 `ernie-4.5-turbo-128k`)、`qianfan_model_deep`(默认沿用 `qianfan_model`)。保留 `qianfan_model` 作 deep 别名
- [ ] Step 2: `llm.py` 增枚举 `TaskKind`(`turn` / `deep_plan`),`generate_turn` 默认用 fast;新增可选参数 `kind`;按 kind 选 model 名
- [ ] Step 3: `_call_qianfan` 接受 `model` 参数
- [ ] Step 4: `test_llm_routing.py`:monkeypatch `_call_qianfan` 捕获 model;`generate_turn(kind=turn)` 用 fast 名;`kind=deep_plan` 用 deep 名
- [ ] Step 5: `pytest -q` pass
- [ ] Step 6: 真实联调:配 fast 模型跑一轮,记录耗时应 < 8s(人工)
- [ ] Step 7: Commit `feat: LLM 任务级模型分流(交互用快模型)`

### Task 1.2: 即时反馈占位

**Files:**
- Modify: `backend/app/api/session_ws.py`
- Modify: `frontend/src/App.tsx`

- [ ] Step 1: 收到 user_utterance 立即发 `{type:'thinking', hint:'正在分析并作画…'}`(已有 thinking,补 hint)
- [ ] Step 2: 前端 thinking 时在目标区显示 shimmer/骨架占位(若已知 focus zone 高亮 pending)
- [ ] Step 3: `npm run build` pass;浏览器人工确认等待态有反馈
- [ ] Step 4: Commit `feat: 思考态即时反馈占位`

---

## Phase 2: 完整 9 zone + 多模板 + goal 路由

### Task 2.1: 补齐 6 个 zone schema

**Files:**
- Modify: `backend/app/templates/family_protection.py`(抽出公共 zone 库)
- Create: `backend/app/templates/zones_library.py`
- Create: `backend/tests/test_zones_library.py`

- [ ] Step 1: 新建 `zones_library.py` 汇总全部 9 zone 定义(id/order/title 双语/JSON Schema)。新增:
  - `income_assets`:`{accounts:[{type,value,unit,note}], total_investable, summary}`
  - `education_fund`:`{children:[{name,location,start_year,annual_cost,years,unit}], total_need, funding_gap, summary}`
  - `retirement_cashflow`:`{retire_age, annual_expense, income_sources:[{name,annual,from_age}], gap_years, summary, unit}`
  - `estate_succession`:`{structures:[{type,beneficiary,jurisdiction,note}], tax_notes, summary}`
  - `cross_border_notes`:`{notes:[{jurisdiction,topic,detail}], summary}`
  - `summary_dashboard`:`{highlights:[{label,value,unit}], action_items:[string], summary}`
- [ ] Step 2: 每个 schema `additionalProperties:false` + required 关键字段
- [ ] Step 3: `family_protection.py` 改为从库引用其 3 个 zone(保持向后兼容)
- [ ] Step 4: `test_zones_library.py`:对每个 zone 用一份合法样例 data 跑 `Draft7Validator` 通过;一份缺 required 的样例失败
- [ ] Step 5: `pytest -q` pass
- [ ] Step 6: Commit `feat: 补齐 9 个 zone 的 JSON Schema 定义`

### Task 2.2: 多模板定义 + goal→template 路由

**Files:**
- Create: `backend/app/templates/registry.py`
- Modify: `backend/app/services/session_store.py`(create 接受 template_id)
- Modify: `backend/app/services/llm.py`(prompt 注入 template 的 zone 子集)
- Modify: `backend/app/api/session_ws.py`(start 接受 goal/template)
- Create: `backend/tests/test_template_registry.py`

- [ ] Step 1: `registry.py` 定义 4 模板及各自 zone 列表:
  - `family-protection`: family_profile, protection_gap, coverage_plan
  - `retirement`: family_profile, income_assets, retirement_cashflow, summary_dashboard
  - `education`: family_profile, education_fund, coverage_plan, summary_dashboard
  - `comprehensive`: 全 9 zone
  - 提供 `template_zone_ids(tid)`、`template_meta()`
- [ ] Step 2: `session_store.create(template_id)` 按模板 init 对应 zone
- [ ] Step 3: `llm.py` 的 `_zone_schemas_text` 只列当前 session 模板的 zone(从 session.template_id 读)
- [ ] Step 4: `session_ws.py` start 支持 `templateId`(缺省 family-protection);新增 `set_template` 消息;`zone_meta` 按 session 模板返回
- [ ] Step 5: `test_template_registry.py`:comprehensive 含 9 zone;retirement 含 retirement_cashflow 不含 coverage_plan
- [ ] Step 6: `pytest -q` pass
- [ ] Step 7: Commit `feat: 多规划模板 + goal→template 路由`

### Task 2.3: 前端 6 个 zone 渲染组件 + 模板选择

**Files:**
- Create: `frontend/src/zones/IncomeAssets.tsx` `EducationFund.tsx` `RetirementCashflow.tsx` `EstateSuccession.tsx` `CrossBorderNotes.tsx` `SummaryDashboard.tsx`
- Modify: `frontend/src/zones/index.tsx`(注册 6 个)
- Modify: `frontend/src/lib/types.ts`(补 6 个 data 类型)
- Modify: `frontend/src/App.tsx`(开场模板/目标选择)

- [ ] Step 1: 为每个新 zone 写纯函数渲染组件(列表/进度条/卡片风格,与现有一致)
- [ ] Step 2: `types.ts` 补对应 interface
- [ ] Step 3: `index.tsx` 注册全部 9 个 renderer
- [ ] Step 4: App 开场加"今天想规划什么"四选一(family/retirement/education/comprehensive),选后发 `set_template`
- [ ] Step 5: `npm run build` pass;浏览器人工确认四模板各能渲染
- [ ] Step 6: Commit `feat: 6 个新 zone 渲染组件 + 开场模板选择`

---

## Phase 3: Zone 依赖管理

### Task 3.1: 依赖声明 + 下游失效提示

**Files:**
- Modify: `backend/app/templates/zones_library.py`(加 dependencies)
- Modify: `backend/app/services/zone_engine.py`
- Modify: `backend/app/services/dialogue.py`
- Modify: `frontend/src/App.tsx`
- Create: `backend/tests/test_zone_dependencies.py`

- [ ] Step 1: zone def 增 `dependencies: [zone_id]`(如 protection_gap 依赖 income_assets;retirement_cashflow 依赖 income_assets)
- [ ] Step 2: `zone_engine.downstream_of(zone_id)` 返回受影响 zone;apply_patch 后把已 filled 的下游标记 `stale`(zone 增 `stale: bool`)
- [ ] Step 3: dialogue 在 zone_update 事件附 `staleDownstream:[zone_id]`
- [ ] Step 4: 前端收到后在下游 zone 角标"上游已变,需更新?"按钮,点了发一条 `user_utterance:"更新<title>"`
- [ ] Step 5: `test_zone_dependencies.py`:改 income_assets 使 filled 的 retirement_cashflow 变 stale
- [ ] Step 6: `pytest -q` pass;`npm run build` pass
- [ ] Step 7: Commit `feat: zone 依赖管理与下游失效提示`

---

## Phase 4: 对话健壮性(PRD §3.3 边界)

### Task 4.1: out_of_scope 自由对话 zone

**Files:**
- Modify: `backend/app/services/dialogue.py`
- Modify: `backend/app/api/session_ws.py`
- Modify: `frontend/src/App.tsx`
- Create: `backend/tests/test_out_of_scope.py`

- [ ] Step 1: intent=out_of_scope 时不动主白板,产出 `{type:'free_chat', narration}` 事件
- [ ] Step 2: 前端在侧栏渲染自由对话气泡(不影响 zone)
- [ ] Step 3: `test_out_of_scope.py`(FakeLLM 返回 out_of_scope):无 zone_update,有 free_chat
- [ ] Step 4: `pytest -q` pass
- [ ] Step 5: Commit `feat: 超范围问题降级为自由对话,不破坏主白板`

### Task 4.2: 沉默提示 + ASR 失败文字确认

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/hooks/useRecorder.ts`

- [ ] Step 1: 前端 60s 无交互 → 显示"还在吗?需要换个话题?"提示条
- [ ] Step 2: ASR 失败(asr_failed)→ 弹出可编辑文字框让用户确认/修改后发送(现仅提示,改为可操作)
- [ ] Step 3: `npm run build` pass;人工确认两路径
- [ ] Step 4: Commit `feat: 60s 沉默提示 + ASR 失败转文字确认`

---

## Phase 5: Session Manager 增强

### Task 5.1: PDF 导出

**Files:**
- Modify: `backend/requirements.txt`(reportlab)
- Create: `backend/app/services/pdf_export.py`
- Modify: `backend/app/main.py`(GET /api/session/{id}/pdf)
- Modify: `frontend/src/App.tsx`(导出按钮)
- Create: `backend/tests/test_pdf_export.py`

- [ ] Step 1: `pdf_export.py`:把 session 各 filled zone 的 data 渲染为带页眉的 PDF(reportlab),返回 bytes
- [ ] Step 2: `main.py` 加路由,Content-Type application/pdf
- [ ] Step 3: 前端"导出 PDF"按钮 → 打开 `/api/session/{id}/pdf`
- [ ] Step 4: `test_pdf_export.py`:对有 2 zone 的 session 生成 PDF,断言 bytes 以 `%PDF` 开头且非空
- [ ] Step 5: `pytest -q` pass
- [ ] Step 6: Commit `feat: session PDF 导出`

### Task 5.2: 只读分享链接 + replay

**Files:**
- Modify: `backend/app/models/schemas.py`(share token + expiry)
- Modify: `backend/app/services/session_store.py`
- Modify: `backend/app/main.py`(GET /api/share/{token})
- Modify: `frontend/src/App.tsx`(分享按钮 + 只读视图)
- Create: `backend/tests/test_share.py`

- [ ] Step 1: session 生成 `share_token`(随机)+ `share_expires_at`(默认 +7 天)
- [ ] Step 2: `/api/share/{token}` 返回脱敏 session(zones + narration,无 contactInfo),过期返回 410
- [ ] Step 3: 前端 `?share=token` 时进只读模式(无输入框,渲染 zones + 对话)
- [ ] Step 4: `test_share.py`:有效 token 返回 zones;过期 token 410
- [ ] Step 5: `pytest -q` pass;`npm run build` pass
- [ ] Step 6: Commit `feat: 只读分享链接(7 天过期)`

---

## Phase 6: LLM 编排完善

### Task 6.1: 单 session 成本追踪 + 上限

**Files:**
- Create: `backend/app/services/cost.py`
- Modify: `backend/app/services/llm.py`
- Modify: `backend/app/models/schemas.py`(session.llm_cost)
- Create: `backend/tests/test_cost.py`

- [ ] Step 1: `cost.py`:按 model 名 + token 数估算费用(可配单价表);累加到 session
- [ ] Step 2: `_call_qianfan` 读 usage(prompt/completion tokens)回传;llm 累计到 session.llm_cost
- [ ] Step 3: 超硬上限($1.50 可配)→ 抛 `BudgetExceeded`,dialogue 降级为礼貌结束
- [ ] Step 4: `test_cost.py`:累加正确;超限抛异常
- [ ] Step 5: `pytest -q` pass
- [ ] Step 6: Commit `feat: 单 session LLM 成本追踪与硬上限`

### Task 6.2: turn 结果缓存 + guardrails 校验

**Files:**
- Modify: `backend/app/services/llm.py`
- Create: `backend/app/services/guardrails.py`
- Create: `backend/tests/test_guardrails.py`

- [ ] Step 1: 缓存键 `(template_id, zone_state_hash, utterance)` → TurnPlan,内存 LRU,24h TTL
- [ ] Step 2: `guardrails.py`:对 narration/zone_data 做禁词校验(具体股票代码、"保证收益"、"必涨"等)→ 命中则改写/追加免责
- [ ] Step 3: dialogue 在产出前过 guardrails
- [ ] Step 4: `test_guardrails.py`:含"保证收益"被改写;含股票代码被拦
- [ ] Step 5: `pytest -q` pass
- [ ] Step 6: Commit `feat: turn 缓存 + 合规 guardrails 后置校验`

---

## Phase 7: RAG 知识库(种子库 + 检索注入)

### Task 7.1: 内存向量检索 + 种子知识库

**Files:**
- Create: `backend/app/services/rag.py`
- Create: `backend/app/data/knowledge_seed.json`
- Modify: `backend/app/services/llm.py`(注入检索结果)
- Modify: `backend/app/models/schemas.py`(KnowledgeChunk)
- Create: `backend/tests/test_rag.py`

- [ ] Step 1: `KnowledgeChunk` 模型(jurisdiction/category/effectiveDate/text/source/confidenceLevel)
- [ ] Step 2: `knowledge_seed.json`:手工 curate 20-40 条 US/HK 公开规则种子(estate tax 阈值、重疾定义、跨境税务一般性条款),每条含 source
- [ ] Step 3: `rag.py`:用千帆 embedding(若无则退化为 BM25/关键词)检索;`retrieve(query, jurisdiction, k)` 返回 chunks
- [ ] Step 4: `llm.py` 把 top-k chunk 文本与 source 注入 system/user prompt;narration 引用来源
- [ ] Step 5: `test_rag.py`:查询"estate tax"召回含 estate 的 chunk;jurisdiction 过滤生效
- [ ] Step 6: `pytest -q` pass
- [ ] Step 7: Commit `feat: RAG 种子知识库 + 检索注入(来源可追溯)`

### Task 7.2: 爬虫小样例(可运行,非全量)

**Files:**
- Create: `backend/scripts/scrape_sample.py`
- Modify: `README.md`(运行说明 + 合规声明)

- [ ] Step 1: `scrape_sample.py`:抓 1-2 个公开监管页(如 IRS estate tax 页),清洗为 KnowledgeChunk 追加到 seed。带 robots/频率注释
- [ ] Step 2: README 写明:全量爬虫与法务 review 属外部工作,本脚本仅样例
- [ ] Step 3: 人工运行一次确认产出 JSON(网络可用时)
- [ ] Step 4: Commit `feat: 知识抓取可运行小样例 + 合规说明`

---

## Phase 8: Broker Lead Funnel(软件闭环 + mock broker)

### Task 8.1: Lead 打分 + 匹配

**Files:**
- Create: `backend/app/services/broker.py`
- Create: `backend/app/data/brokers_mock.json`
- Modify: `backend/app/models/schemas.py`(Lead/Broker/AssetTier)
- Create: `backend/tests/test_broker.py`

- [ ] Step 1: `Lead`/`Broker` 模型(对齐 PRD §5)
- [ ] Step 2: `brokers_mock.json`:5 个 mock broker(地区/语言/acceptedLeadTiers)
- [ ] Step 3: `broker.py`:`score_lead(session)`(资产档×完成度×意向)→ tier;`match(lead)` 按地区+语言+tier 选 broker;`price_for(tier)`($50/$150/$300)
- [ ] Step 4: `test_broker.py`:高资产+高完成度→hnw tier;匹配到接受该 tier 且语言匹配的 broker
- [ ] Step 5: `pytest -q` pass
- [ ] Step 6: Commit `feat: broker lead 打分与匹配(mock broker)`

### Task 8.2: Handoff 流程 + 反作弊 + Broker Portal

**Files:**
- Modify: `backend/app/api/session_ws.py`(lead capture 消息)
- Create: `backend/app/api/broker_portal.py`(REST:list leads / claim)
- Modify: `backend/app/main.py`(挂 broker 路由)
- Create: `frontend/src/BrokerPortal.tsx`(简单后台页,路由 `?portal=1`)
- Modify: `frontend/src/App.tsx`(CTA→采集联系方式→handoff 文案)
- Create: `backend/tests/test_handoff.py`

- [ ] Step 1: 前端 finalize CTA"找经纪人深入"→ 弹采集表单(姓名/联系方式/偏好)→ 发 `lead_capture`
- [ ] Step 2: 后端创建 Lead、match、记录;回 handoff 文案("已为你匹配 X,48h 内联系,她已看过你的草图")
- [ ] Step 3: 反作弊:同邮箱/手机号多次 cancel 计数,超阈值标 risky 不再匹配
- [ ] Step 4: `broker_portal.py`:GET /api/broker/leads(脱敏列表+session 白板)、POST /api/broker/leads/{id}/claim(48h SLA 计时)
- [ ] Step 5: `BrokerPortal.tsx`:列出 leads、看 session zones、claim 按钮
- [ ] Step 6: `test_handoff.py`:lead_capture→Lead matched;重复 cancel→risky
- [ ] Step 7: `pytest -q` pass;`npm run build` pass;浏览器确认 portal
- [ ] Step 8: Commit `feat: lead handoff + 反作弊 + broker portal(mock)`

---

## Phase 9: Onboarding / Voice persona / i18n / Premium 占位

### Task 9.1: Onboarding + Voice persona

**Files:**
- Modify: `frontend/src/App.tsx`(首启 onboarding:语言+隐私承诺+用途)
- Modify: `backend/app/services/speech.py`(persona→百度 per 映射)
- Modify: `backend/app/api/session_ws.py`(set_persona)
- Create: `frontend/src/components/Onboarding.tsx`

- [ ] Step 1: `Onboarding.tsx`:语言选择、隐私承诺、用途介绍三屏,localStorage 记 onboarded
- [ ] Step 2: persona 三选(资深绅士=per1/亲切阿姨=per0/专业青年=per3),set_persona 存 session,TTS 用对应 per
- [ ] Step 3: `npm run build` pass;人工确认首启流程与音色切换(需语音 key)
- [ ] Step 4: Commit `feat: onboarding 流程 + 语音 persona 选择`

### Task 9.2: i18n 文案外置 + Premium gating 占位

**Files:**
- Create: `frontend/src/lib/i18n.ts`
- Modify: `frontend/src/App.tsx`(替换硬编码中文文案)
- Modify: `backend/app/models/schemas.py`(User.tier free/premium)
- Modify: `frontend/src/App.tsx`(premium-only 功能加锁:多场景对比/PDF)

- [ ] Step 1: `i18n.ts`:zh/en 文案表 + `t(key, lang)`;App 文案走 t()
- [ ] Step 2: Premium 占位:PDF 导出/模板对比标"Premium",free 用户点击提示升级(不接真实计费)
- [ ] Step 3: `npm run build` pass
- [ ] Step 4: Commit `feat: i18n 文案外置 + Premium gating 占位`

---

## 完成后
- 运行全量 `pytest -q` 与 `npm run build` 全绿
- 使用 superpowers:finishing-a-development-branch 收尾
- 更新 README 里程碑勾选与"外部对接 TODO"清单

## 自检覆盖(对照 PRD)
- §2.2 模块清单:M3 dialogue✓ M4 zone engine(9 zone)✓ M5 编排(分流/cost/cache/guardrails)✓ M6 渲染✓ M7 RAG✓ M8 TTS persona✓ M9 session(PDF/share)✓ M10 broker funnel✓ M11 爬虫样例✓ M2 ASR(REST 已有,streaming 标为后续)
- §3.3 边界:断网autosave✓ out_of_scope✓ 沉默✓ ASR失败✓ HTML破损降级✓
- §4 各模块验收标准:zone schema 校验、纯函数渲染、成本上限、来源可追溯 —— 对应 Phase 测试
- 标注外部:全量爬虫/真实 broker/RN/云部署/Stripe 计费
