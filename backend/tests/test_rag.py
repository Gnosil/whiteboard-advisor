from app.services import rag


def test_retrieve_estate_tax():
    hits = rag.retrieve("美国遗产税怎么规划", jurisdiction="US")
    assert hits
    assert any("estate" in h.id or "遗产" in h.text for h in hits)


def test_jurisdiction_filter_excludes_other():
    hits = rag.retrieve("遗产税", jurisdiction="HK")
    # 不应召回纯 US-only 的 chunk(如 us-situs-assets-nra),应含 HK 或 global
    for h in hits:
        assert h.jurisdiction in ("HK", "global")


def test_no_match_returns_empty():
    assert rag.retrieve("披萨外卖优惠券", jurisdiction="HK") == []


def test_context_block_includes_source():
    block = rag.context_block("重疾险保额", jurisdiction="global")
    assert block
    assert "来源" in block
