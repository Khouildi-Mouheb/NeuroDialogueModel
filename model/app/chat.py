import sys
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# -------------------------------------------------------------------
# Path fix (important for your project structure)
# -------------------------------------------------------------------
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neurodialogue-api")

# -------------------------------------------------------------------
# Your project imports
# -------------------------------------------------------------------
from generation.agents.cloudBasedGenerator import CloudBasedGenerator

# ────────────────────────────────────────────────────────────────
# COMMENTED OUT → analysis & verification agents (to save memory)
# ────────────────────────────────────────────────────────────────
# from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
# from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent
#
# from verification.agents.safetyVerificator import SafetyVerificator
# from verification.agents.empathyVerificator import EmpathyVerificator
# from verification.agents.appropriatenessVerificator import AppropriatenessVerificator
# from verification.strategies.mlVerificationStrategy import MLVerificationStrategy
# from verification.config.verificationConfig import VerificationConfig

from app.chatService import ChatService

# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------
app = FastAPI(
    title="NeuroDialogue AI API (Generator Only Mode)",
    description="Minimal mode: only cloud-based generation (no emotion/intent/verification)",
    version="2.0.0-minimal"
)

# -------------------------------------------------------------------
# CORS – allow frontend (restrict origins in production!)
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ← Change to specific domains later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Request / Response models
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    text: str
    conversation_id: str | None = None      # optional – for future multi-turn

class ChatResponse(BaseModel):
    status: str
    data: str
    error: str | None = None

# -------------------------------------------------------------------
# Global service (loaded once at startup)
# -------------------------------------------------------------------
chat_service: ChatService | None = None

@app.on_event("startup")
def startup_event():
    global chat_service
    logger.info("🚀 Starting NeuroDialogue services (minimal mode)...")

    try:
        logger.info("Loading CloudBasedGenerator...")
        generator = CloudBasedGenerator()

        # ────────────────────────────────────────────────────────────────
        # COMMENTED OUT → no analysis or verification agents
        # ────────────────────────────────────────────────────────────────
        # emotion_agent = EmotionDetectionAgent()
        # intent_agent = IntentNeedsAgent()
        #
        # verification_config = VerificationConfig(...)
        # verificators = [SafetyVerificator(...), ...]
        # verification_strategy = MLVerificationStrategy(...)

        # Pass only the generator to ChatService
        # (you may need to temporarily adjust ChatService.__init__ to accept None or remove unused params)
        chat_service = ChatService(
            generator=generator,
            emotion_agent=None,           # ← temporary – adjust your ChatService code
            intent_agent=None,            # ← temporary
            verification_strategy=None,   # ← temporary
            verificators=None             # ← temporary
        )

        logger.info("✅ NeuroDialogue initialized successfully (generator only)")

    except Exception as e:
        logger.critical("Failed to initialize services", exc_info=True)
        raise RuntimeError("Startup failed") from e

# -------------------------------------------------------------------
# Health check (fast & always available)
# -------------------------------------------------------------------
@app.get("/health")
@app.get("/healthz")
def health_check():
    return {"status": "healthy", "mode": "generator-only", "service": "neurodialogue-model"}

# -------------------------------------------------------------------
# Main chat endpoint – POST /chat
# -------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    if chat_service is None:
        raise HTTPException(status_code=503, detail="AI service not initialized")

    logger.info(f"💬 Incoming: {request.text!r} | conv: {request.conversation_id}")

    try:
        raw_result = chat_service.generate_response(request.text)
        
        # Extract string response
        response_text = (
            raw_result.get("response")
            or raw_result.get("text")
            or raw_result.get("message")
            or str(raw_result)
        ).strip()

        if not response_text:
            response_text = "No response generated"

        return ChatResponse(
            status="success",
            data=response_text,
            error=None
        )
    except Exception as e:
        logger.error("Generation failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# -------------------------------------------------------------------
# Run locally (development)
# -------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",           # ← change "main" to your actual filename if different
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )