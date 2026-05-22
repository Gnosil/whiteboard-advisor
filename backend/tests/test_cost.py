import pytest

from app.services import cost


def test_estimate_known_model():
    c = cost.estimate("ernie-4.5-turbo-128k", 1000, 1000)
    assert c == pytest.approx(0.0008 + 0.0024)


def test_estimate_unknown_uses_default():
    c = cost.estimate("mystery-model", 1000, 0)
    assert c == pytest.approx(0.002)


def test_check_budget_raises_over_cap():
    cost.check_budget(0.0)  # 不抛
    with pytest.raises(cost.BudgetExceeded):
        cost.check_budget(cost.SESSION_HARD_CAP_USD)
