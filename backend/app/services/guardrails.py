"""合规 guardrails:对 LLM 产出的 narration 做后置校验与软化(PRD §4.5)。

- 禁用绝对化/承诺收益措辞 → 软化改写
- 检测疑似具体证券代码 → 记违规并追加免责
不做硬阻断(避免误伤),以"改写 + 追加免责"为主,违规计入日志/可观测。
"""

from __future__ import annotations

import re

# 绝对化 / 承诺类措辞 → 软化替换
_REPLACEMENTS = {
    "保证收益": "潜在回报(不保证)",
    "稳赚": "有机会获益(不保证)",
    "包赚": "有机会获益(不保证)",
    "零风险": "风险较低(并非无风险)",
    "必涨": "可能上行(不确定)",
    "必跌": "可能下行(不确定)",
    "一定能": "有机会",
}

# 疑似具体证券代码:$TICKER / 6 位 A 股代码 / 5 位港股代码
_TICKER_RES = [
    re.compile(r"\$[A-Za-z]{1,5}\b"),
    re.compile(r"\b\d{6}\b"),
    re.compile(r"\b\d{5}\.HK\b", re.IGNORECASE),
]

_DISCLAIMER = "(以上为一般性思路,不构成具体投资建议,请咨询持牌专业人士。)"


def scan(text: str) -> list[str]:
    violations = []
    for bad in _REPLACEMENTS:
        if bad in text:
            violations.append(f"banned_phrase:{bad}")
    for rx in _TICKER_RES:
        if rx.search(text):
            violations.append(f"ticker_like:{rx.pattern}")
    return violations


def sanitize(text: str) -> tuple[str, list[str]]:
    """返回 (改写后的文本, 违规列表)。"""
    violations = scan(text)
    out = text
    for bad, good in _REPLACEMENTS.items():
        out = out.replace(bad, good)
    if any(v.startswith("ticker_like") for v in violations) and _DISCLAIMER not in out:
        out = f"{out} {_DISCLAIMER}"
    return out, violations
