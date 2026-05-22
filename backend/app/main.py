import logging

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.session_ws import router as session_router
from app.config import settings
from app.services import pdf_export, session_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whiteboard-advisor")

app = FastAPI(title="WhiteboardAdvisor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "llm": settings.has_llm,
        "speech": settings.has_speech,
    }


@app.get("/api/session/{session_id}/pdf")
async def session_pdf(session_id: str) -> Response:
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    pdf = pdf_export.render_session_pdf(session)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="plan-{session_id[:8]}.pdf"'},
    )
