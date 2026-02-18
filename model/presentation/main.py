"""
Main presentation entry point - FastAPI server.
"""
import sys
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add model directory to path for imports
sys.path.insert(
    0,
    os.path.abspath(os.path.dirname(__file__))
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neurodialogue-api")

# Import from application layer (orchestrator)
from application.chat_orchestrator import ChatOrchestrator

# Import from adapters
from adapters.generation.cloud_based_generator import CloudBasedGenerator
from adapters.analysis.emotion_detection_adapter import EmotionDetectionAdapter
from adapters.analysis.intent_and_needs_adapter import IntentAndNeedsAdapter
from adapters.verification.safety_verificator_adapter import SafetyVerificatorAdapter
from adapters.verification.empathy_verificator_adapter import EmpathyVerificatorAdapter
from adapters.verification.appropriateness_verificator_adapter import AppropriatenessVerificatorAdapter
from adapters.verification.ml_verification_strategy_adapter import MLVerificationStrategyAdapter
from adapters.verification.config.verification_config import VerificationConfig

app = FastAPI(
    title="NeuroDialogue AI API (Hexagonal Architecture)",
    description="Clean architecture with strict port/adapter separation",
    version="3.0.0-hexagonal"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    text: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    status: str
    data: str
    error: str | None = None


chat_orchestrator: ChatOrchestrator | None = None


@app.on_event("startup")
def startup_event():
    global chat_orchestrator
    logger.info("🚀 Starting NeuroDialogue with Hexagonal Architecture...")

    try:
        logger.info("Initializing adapters...")
        
        # Initialize adapters (implements ports)
        llm_adapter = CloudBasedGenerator()
        emotion_adapter = EmotionDetectionAdapter()
        intent_adapter = IntentAndNeedsAdapter()
        
        # Verification config (adapter-specific, doesn't leak to domain)
        verification_config = VerificationConfig(
            safety_threshold=0.8,
            empathy_threshold=0.6,
            appropriateness_threshold=0.7,
            enable_fallback=True
        )
        
        # Verification adapters
        verificators = [
            SafetyVerificatorAdapter(threshold=verification_config.safety_threshold),
            EmpathyVerificatorAdapter(threshold=verification_config.empathy_threshold),
            AppropriatenessVerificatorAdapter(threshold=verification_config.appropriateness_threshold)
        ]
        
        # Verification strategy adapter
        verification_strategy = MLVerificationStrategyAdapter(
            score_weights=verification_config.score_weights,
            enable_fallback=verification_config.enable_fallback
        )

        # Initialize application orchestrator with port-based dependencies
        chat_orchestrator = ChatOrchestrator(
            llm_port=llm_adapter,
            emotion_port=emotion_adapter,
            intent_port=intent_adapter,
            verification_strategy_port=verification_strategy,
            verificators=verificators
        )

        logger.info("✅ NeuroDialogue initialized successfully")

    except Exception as e:
        logger.critical("Failed to initialize services", exc_info=True)
        raise RuntimeError("Startup failed") from e


@app.get("/health")
@app.get("/healthz")
def health_check():
    return {"status": "healthy", "architecture": "hexagonal", "service": "neurodialogue-model"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    if chat_orchestrator is None:
        raise HTTPException(status_code=503, detail="AI service not initialized")

    logger.info(f"💬 Incoming: {request.text!r} | conv: {request.conversation_id}")

    try:
        # Call application orchestrator
        result = chat_orchestrator.orchestrate(request.text)
        
        response_text = (
            result.get("response")
            or result.get("text")
            or result.get("message")
            or str(result)
        ).strip()

        if not response_text:
            response_text = "No response generated"

        return ChatResponse(
            status="success",
            data=response_text,
            error=None
        )
    except Exception as e:
        logger.error("Orchestration failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
