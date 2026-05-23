"""百度智能云语音:ASR(短语音识别)+ TTS(在线合成)。

鉴权:API_KEY + SECRET_KEY → access_token(缓存,提前 60s 过期)。
无凭证时降级:ASR 返回 None(前端走文字输入),TTS 返回 None(前端不播音)。

录音约定:前端采集 16kHz / 单声道 / 16-bit PCM,base64 传入。
"""

from __future__ import annotations

import base64
import logging
import re
import time
from typing import Optional

import httpx

from app.config import settings
from app.models.schemas import Language

logger = logging.getLogger("whiteboard-advisor.speech")

_TOKEN_CACHE: dict[str, float | str] = {}

# 百度 ASR dev_pid:普通话 1537 / 英语 1737 / 粤语 1637
ASR_PID = {Language.zh: 1537, Language.en: 1737}
# 百度 TTS 发音人:0 女声 / 1 男声 / 3 度逍遥 / 4 度丫丫
TTS_VOICE_MALE = 1

# persona → 百度 per
PERSONA_VOICE = {
    "gentleman": 1,   # 资深绅士(男声)
    "auntie": 0,      # 亲切阿姨(女声)
    "young_pro": 3,   # 专业青年(度逍遥)
}


def voice_for_persona(persona: str) -> int:
    return PERSONA_VOICE.get(persona, TTS_VOICE_MALE)


_SENT_RE = re.compile(r"[^。！？!?\n]*[。！？!?\n]")


def pop_sentences(buf: str) -> tuple[list[str], str]:
    """从流式 narration 缓冲里切出完整句子,返回 (完整句列表, 剩余未完成片段)。
    用于流式 TTS:每完成一句就合成一句。"""
    sentences: list[str] = []
    last = 0
    for m in _SENT_RE.finditer(buf):
        s = m.group()
        if s.strip():
            sentences.append(s)
        last = m.end()
    return sentences, buf[last:]


async def _get_token() -> Optional[str]:
    if not settings.has_speech:
        return None
    now = time.time()
    if _TOKEN_CACHE.get("token") and float(_TOKEN_CACHE.get("exp", 0)) > now:
        return str(_TOKEN_CACHE["token"])
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": settings.baidu_speech_api_key,
        "client_secret": settings.baidu_speech_secret_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    token = data.get("access_token")
    if not token:
        logger.error("获取 access_token 失败: %s", data)
        return None
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["exp"] = now + int(data.get("expires_in", 2592000)) - 60
    return token


async def transcribe(audio_b64: str, language: Language, rate: int = 16000) -> Optional[str]:
    token = await _get_token()
    if not token:
        return None
    raw = base64.b64decode(audio_b64)
    payload = {
        "format": "pcm",
        "rate": rate,
        "channel": 1,
        "cuid": "whiteboard-advisor",
        "token": token,
        "dev_pid": ASR_PID.get(language, 1537),
        "speech": audio_b64,
        "len": len(raw),
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post("https://vop.baidu.com/server_api", json=payload)
        resp.raise_for_status()
        data = resp.json()
    if data.get("err_no") != 0:
        logger.warning("ASR 失败: %s", data)
        return None
    result = data.get("result") or []
    return result[0] if result else None


async def synthesize(text: str, language: Language, voice: int = TTS_VOICE_MALE) -> Optional[str]:
    """返回 base64 编码的 mp3,失败返回 None。"""
    token = await _get_token()
    if not token or not text.strip():
        return None
    data = {
        "tex": text,
        "tok": token,
        "cuid": "whiteboard-advisor",
        "ctp": 1,
        "lan": "zh",  # 百度 zh 通道兼容中英混读
        "spd": 5,
        "pit": 5,
        "vol": 5,
        "per": voice,
        "aue": 3,  # mp3
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post("https://tsn.baidubce.com/text2audio", data=data)
    ctype = resp.headers.get("Content-Type", "")
    if "audio" not in ctype:
        logger.warning("TTS 失败: %s", resp.text[:200])
        return None
    return base64.b64encode(resp.content).decode("ascii")
