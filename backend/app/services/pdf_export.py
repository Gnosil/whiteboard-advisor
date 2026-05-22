"""把 session 的已填充 zone 渲染成带页眉的 PDF(reportlab,内置中文 CID 字体)。"""

from __future__ import annotations

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

from app.models.schemas import Session
from app.templates import registry
from app.templates import zones_library as zl

_FONT = "STSong-Light"
_registered = False


def _ensure_font() -> None:
    global _registered
    if not _registered:
        pdfmetrics.registerFont(UnicodeCIDFont(_FONT))
        _registered = True


def _flatten(data: dict, indent: int = 0) -> list[str]:
    """把 zone 的结构化 data 平铺成可打印的文本行。"""
    lines: list[str] = []
    pad = "  " * indent
    for k, v in data.items():
        if isinstance(v, list):
            lines.append(f"{pad}{k}:")
            for item in v:
                if isinstance(item, dict):
                    parts = [f"{ik}={iv}" for ik, iv in item.items() if iv not in (None, "")]
                    lines.append(f"{pad}  - {', '.join(parts)}")
                else:
                    lines.append(f"{pad}  - {item}")
        elif isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            lines.extend(_flatten(v, indent + 1))
        elif v not in (None, ""):
            lines.append(f"{pad}{k}: {v}")
    return lines


def render_session_pdf(session: Session) -> bytes:
    _ensure_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    def header():
        nonlocal y
        c.setFont(_FONT, 16)
        c.drawString(20 * mm, height - 18 * mm, "WhiteboardAdvisor · 规划草图")
        c.setFont(_FONT, 9)
        c.drawString(20 * mm, height - 23 * mm, f"Session {session.id[:8]} · 模板 {session.template_id}")
        c.line(20 * mm, height - 25 * mm, width - 20 * mm, height - 25 * mm)

    def line(text: str, size: int = 10, gap: float = 6):
        nonlocal y
        if y < 25 * mm:
            c.showPage()
            header()
            y = height - 32 * mm
        c.setFont(_FONT, size)
        c.drawString(20 * mm, y, text[:90])
        y -= gap * mm

    header()
    y = height - 32 * mm

    for zdef in registry.template_zone_defs(session.template_id):
        zone = session.zones.get(zdef["id"])
        if not zone or not zone.data:
            continue
        line(zdef["title"]["zh"], size=13, gap=8)
        for ln in _flatten(zone.data):
            line(ln, size=10, gap=5.5)
        y -= 3 * mm

    line("本草图为一般性思路,具体产品与方案请咨询持牌经纪人。", size=9, gap=6)
    c.showPage()
    c.save()
    return buf.getvalue()
