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
from analysis.agents.emotionDetectionAgent import EmotionDetectionAgent
from analysis.agents.intentAndNeedsAgent import IntentNeedsAgent

from verification.agents.safetyVerificator import SafetyVerificator
from verification.agents.empathyVerificator import EmpathyVerificator
from verification.agents.appropriatenessVerificator import AppropriatenessVerificator
from verification.strategies.mlVerificationStrategy import MLVerificationStrategy
from verification.config.verificationConfig import VerificationConfig

from app.chatService import ChatService

# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------
app = FastAPI(
    title="NeuroDialogue AI API",
    description="Emotion-aware conversational AI service",
    version="2.0.0"
)

# -------------------------------------------------------------------
# CORS – allow frontend (restrict origins in production!)
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ← Change to specific domains later (e.g. ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Request / Response models
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    text: str
    conversation_id: str | None = None      # optional – useful for multi-turn context later

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
    logger.info("🚀 Starting NeuroDialogue services...")

    try:
        generator = CloudBasedGenerator()
        logger.info("🚀 Starting generation services...")
        print("🚀 Starting generation services...")
        emotion_agent = EmotionDetectionAgent()
        logger.info("🚀 Starting emotion detection services...")
        print("🚀 Starting emotion detection services...")
        intent_agent = IntentNeedsAgent()
        logger.info("🚀 Starting intent & needs services...")
        print("🚀 Starting intent & needs services...")

        verification_config = VerificationConfig(
            safety_threshold=0.8,
            empathy_threshold=0.6,
            appropriateness_threshold=0.7,
            enable_fallback=True
        )
        logger.info("🚀 Starting verifcation config...")
        print("🚀 Starting verifcation config...")

        verificators = [
            SafetyVerificator(threshold=verification_config.safety_threshold),
            EmpathyVerificator(threshold=verification_config.empathy_threshold),
            AppropriatenessVerificator(threshold=verification_config.appropriateness_threshold),
        ]
        logger.info("🚀 Starting verifcation services...")
        print("🚀 Starting verifcation services...")

        verification_strategy = MLVerificationStrategy(
            score_weights=verification_config.score_weights,
            enable_fallback=verification_config.enable_fallback
        )

        chat_service = ChatService(
            generator=generator,
            emotion_agent=emotion_agent,
            intent_agent=intent_agent,
            verification_strategy=verification_strategy,
            verificators=verificators
        )

        logger.info("✅ NeuroDialogue initialized successfully")
    except Exception as e:
        logger.critical("Failed to initialize services", exc_info=True)
        raise RuntimeError("Startup failed") from e

# -------------------------------------------------------------------
# Health check
# -------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "neurodialogue-model"}

# -------------------------------------------------------------------
# Main chat endpoint – POST /chat (recommended for chat APIs)
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
        
        # Extract the actual string response – adjust key name if different
        response_text = raw_result.get("response", "") if isinstance(raw_result, dict) else str(raw_result)
        
        if not response_text:
            response_text = "No response generated"

        return ChatResponse(
            status="success",
            data=response_text
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
        "chat:app",           
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )