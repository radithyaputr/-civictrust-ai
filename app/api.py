"""
CivicTrust AI - API Router
Main API endpoints with security validation and proper error handling.
"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Depends
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any

from app.agents.orchestrator import AgentOrchestrator
from app.config import settings
from app.utils.security import (
    sanitize_input,
    detect_prompt_injection,
    validate_language_code,
    validate_api_key,
    RateLimiter,
)

logger = logging.getLogger(__name__)

router = APIRouter()
orchestrator = AgentOrchestrator()
rate_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
)


async def verify_api_key(request: Request):
    """Dependency for API key authentication."""
    if not settings.API_KEY_REQUIRED:
        return True
    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="API key tidak valid. Sertakan X-API-Key header atau Authorization: Bearer <key>",
        )
    return True


async def check_rate_limit(request: Request):
    """Dependency for rate limiting."""
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Terlalu banyak permintaan. Silakan coba lagi dalam 60 detik.",
        )


# --- Request/Response Models ---

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "id"
    user_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        sanitized = sanitize_input(v)
        if not sanitized:
            raise ValueError("Pesan tidak boleh kosong")
        injection = detect_prompt_injection(sanitized)
        if injection["injection_detected"]:
            raise ValueError("Pesan mengandung pola yang tidak diizinkan")
        return sanitized

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if not validate_language_code(v):
            raise ValueError(f"Bahasa '{v}' tidak didukung")
        return v


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0
    reasoning_path: List[str] = []
    trust_score: float = 0.0
    disclaimer: Optional[str] = None
    language: str = "id"
    latency: float = 0.0


class FactCheckRequest(BaseModel):
    statement: str
    language: str = "id"

    @field_validator("statement")
    @classmethod
    def validate_statement(cls, v):
        sanitized = sanitize_input(v)
        if not sanitized:
            raise ValueError("Pernyataan tidak boleh kosong")
        return sanitized

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if not validate_language_code(v):
            raise ValueError(f"Bahasa '{v}' tidak didukung")
        return v


class FactCheckResponse(BaseModel):
    statement: str
    verdict: str
    confidence: float
    sources: List[Any] = []
    explanation: str


class DocumentIngestRequest(BaseModel):
    document_id: str
    content: str
    source: str
    source_type: str
    language: str = "id"
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        allowed = ["law", "regulation", "ministry", "who", "un", "government", "news", "general"]
        if v not in allowed:
            raise ValueError(f"source_type harus salah satu dari: {allowed}")
        return v


class TranslationRequest(BaseModel):
    text: str
    source_language: str = "id"
    target_language: str = "en"

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        sanitized = sanitize_input(v, max_length=2000)
        if not sanitized:
            raise ValueError("Teks tidak boleh kosong")
        return sanitized


class VoiceRequest(BaseModel):
    audio_base64: str
    language: str = "id"


class VoiceResponse(BaseModel):
    text: str
    language: str
    confidence: float


class AnalyticsResponse(BaseModel):
    total_queries: int
    accuracy: float
    precision: float
    recall: float
    hallucination_rate: float
    citation_coverage: float
    avg_latency: float
    trust_score_avg: float


# --- API Endpoints ---

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI Chat",
    description="Process a user message through the multi-agent pipeline",
)
async def chat(
    request: ChatRequest,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Main chat endpoint for AI assistant with security validation."""
    try:
        result = await orchestrator.process_message(
            message=request.message,
            session_id=request.session_id,
            language=request.language,
            user_id=request.user_id,
        )
        return ChatResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server.")


@router.post(
    "/fact-check",
    response_model=FactCheckResponse,
    summary="Fact Check",
    description="Verify a statement against official sources",
)
async def fact_check(
    request: FactCheckRequest,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Fact-check a statement against official sources."""
    try:
        result = await orchestrator.fact_check(
            statement=request.statement,
            language=request.language,
        )
        return FactCheckResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fact-check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan saat verifikasi fakta.")


@router.post(
    "/documents/ingest",
    summary="Ingest Document",
    description="Ingest a document into the vector database",
)
async def ingest_document(
    request: DocumentIngestRequest,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Ingest a document into the vector database."""
    try:
        from app.rag.ingestion import DocumentIngestion
        ingestion = DocumentIngestion()
        await ingestion.ingest(
            document_id=request.document_id,
            content=request.content,
            source=request.source,
            source_type=request.source_type,
            language=request.language,
            metadata=request.metadata,
        )
        return {"status": "success", "document_id": request.document_id}
    except Exception as e:
        logger.error(f"Document ingest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal mengingest dokumen.")


@router.post("/translate", summary="Translate Text")
async def translate(
    request: TranslationRequest,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Translate text between supported languages."""
    try:
        from app.modules.translation import TranslationModule
        translator = TranslationModule()
        translated = await translator.translate(
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language,
        )
        return {
            "original_text": request.text,
            "translated_text": translated,
            "source_language": request.source_language,
            "target_language": request.target_language,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal menerjemahkan teks.")


@router.post(
    "/voice/recognize",
    response_model=VoiceResponse,
    summary="Speech Recognition",
)
async def recognize_speech(
    request: VoiceRequest,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Convert speech to text."""
    try:
        from app.modules.voice import VoiceModule
        voice = VoiceModule()
        result = await voice.speech_to_text(
            audio_base64=request.audio_base64,
            language=request.language,
        )
        return VoiceResponse(**result)
    except Exception as e:
        logger.error(f"Voice recognition error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal memproses suara.")


@router.post("/vision/ocr", summary="OCR from Image")
async def ocr_image(
    file: UploadFile = File(...),
    language: str = Form("id"),
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Extract text from image using OCR."""
    if not validate_language_code(language):
        raise HTTPException(status_code=400, detail=f"Bahasa '{language}' tidak didukung")

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")

    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 10MB")

    try:
        from app.modules.vision import VisionModule
        vision = VisionModule()
        result = await vision.extract_text(content, language)
        return result
    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal memproses gambar.")


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Analytics Dashboard",
)
async def get_analytics(
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Get AI analytics dashboard metrics."""
    try:
        from app.modules.analytics import AnalyticsModule
        analytics = AnalyticsModule()
        metrics = await analytics.get_metrics()
        return AnalyticsResponse(**metrics)
    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal memuat data analitik.")


@router.get("/sessions/{session_id}/history", summary="Session History")
async def get_session_history(
    session_id: str,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Get conversation history for a session."""
    try:
        from app.modules.memory import MemoryModule
        memory = MemoryModule()
        history = await memory.get_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Session history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal memuat riwayat sesi.")


@router.delete("/sessions/{session_id}", summary="Clear Session")
async def clear_session(
    session_id: str,
    _=Depends(check_rate_limit),
    __=Depends(verify_api_key),
):
    """Clear conversation history for a session."""
    try:
        from app.modules.memory import MemoryModule
        memory = MemoryModule()
        await memory.clear(session_id)
        return {"status": "success", "session_id": session_id}
    except Exception as e:
        logger.error(f"Session clear error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal menghapus riwayat sesi.")