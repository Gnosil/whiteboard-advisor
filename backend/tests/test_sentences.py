from app.services import speech


def test_pop_complete_sentences():
    sents, rest = speech.pop_sentences("你好。世界!还有")
    assert sents == ["你好。", "世界!"]
    assert rest == "还有"


def test_no_complete_sentence():
    sents, rest = speech.pop_sentences("还没说完")
    assert sents == []
    assert rest == "还没说完"


def test_newline_is_boundary():
    sents, rest = speech.pop_sentences("第一行\n第二行")
    assert sents == ["第一行\n"]
    assert rest == "第二行"


def test_incremental_accumulation():
    # 模拟流式:逐块累加,边界处吐句
    buf = ""
    out = []
    for chunk in ["我把寿", "险保额上", "调到200万。", "因为要覆", "盖学费。"]:
        buf += chunk
        sents, buf = speech.pop_sentences(buf)
        out.extend(sents)
    assert out == ["我把寿险保额上调到200万。", "因为要覆盖学费。"]
    assert buf == ""
