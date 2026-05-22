"""LLM 成本估算与单 session 预算控制(PRD §4.5:目标 < $0.50,硬上限 $1.50)。"""

from __future__ import annotations

# 每千 token 估算单价 (USD)。粗略值,仅用于成本护栏,非账单依据。
PRICE_PER_1K: dict[str, tuple[float, float]] = {
    # model: (prompt, completion)
    "ernie-4.5-turbo-128k": (0.0008, 0.0024),
    "deepseek-v4-pro": (0.004, 0.016),
}
_DEFAULT_PRICE = (0.002, 0.006)

SESSION_HARD_CAP_USD = 1.50


class BudgetExceeded(Exception):
    pass


def estimate(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p_in, p_out = PRICE_PER_1K.get(model, _DEFAULT_PRICE)
    return (prompt_tokens / 1000.0) * p_in + (completion_tokens / 1000.0) * p_out


def check_budget(current_cost: float) -> None:
    if current_cost >= SESSION_HARD_CAP_USD:
        raise BudgetExceeded(f"session LLM 成本已达上限 ${SESSION_HARD_CAP_USD}")
