from app.services import guardrails


def test_banned_phrase_rewritten():
    out, violations = guardrails.sanitize("这个产品保证收益,稳赚不赔。")
    assert "保证收益" not in out
    assert "稳赚" not in out
    assert any(v.startswith("banned_phrase") for v in violations)


def test_ticker_flagged_and_disclaimer_added():
    out, violations = guardrails.sanitize("建议买入 600519,长期持有。")
    assert any(v.startswith("ticker_like") for v in violations)
    assert "请咨询持牌专业人士" in out


def test_clean_text_untouched():
    out, violations = guardrails.sanitize("我们看看你的家庭保障缺口。")
    assert violations == []
    assert out == "我们看看你的家庭保障缺口。"
