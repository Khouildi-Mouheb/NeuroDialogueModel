import sys
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.domain.userQuery import UserQuery
from core.domain.userState import UserState
from core.context.generatorContext import GeneratorContext
from infrastructure.agents.cloudBasedGenerator import CloudBasedGenerator
from infrastructure.agents.emotionDetectionAgent import EmotionDetectionAgent
from infrastructure.agents.intentAndNeedsAgent import IntentNeedsAgent

# Create FastAPI app
app = FastAPI(
    title="NeuroDialogue Model API",
    description="API for emotion-aware chat",
    version="2.0.0"
)

# CORS - Allow your Django domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
generator = CloudBasedGenerator()
emotionsDetector = EmotionDetectionAgent()
intentAndNeedsDetector = IntentNeedsAgent()

@app.get("/")
def read_root():
    return {
        "message": "NeuroDialogue AI API",
        "status": "online",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "neurodialogue-model"}

@app.get("/chat_final")
def chat_final(text: str = Query(..., min_length=1, max_length=2000)):
    """Complete chat response with emotion detection"""
    try:
        logger.info(f"Received query: {text}")
        
        # Create user query
        query = UserQuery(text=text)
        
        # Detect emotions
        logger.info("Detecting emotions...")
        emotionsResult = emotionsDetector.detect_emotions(query, top_k=3)
        
        # Analyze intent
        logger.info("Analyzing intent...")
        intentAndNeedsResult = intentAndNeedsDetector.analyze(text)
        
        # Create user state
        userState = UserState(emotions=emotionsResult)
        
        # Create generator context
        generatorContext = GeneratorContext(
            user_query=query,
            user_state=userState
        )
        
        # Generate response
        logger.info("Generating response...")
        prompt = generatorContext.format_context_for_prompt()
        full_response = ""
        for token in generator.stream(prompt=prompt):
            full_response += token
        
        logger.info("Response generated successfully")
        
        return {
            "response": full_response,
            "query": text,
            "analysis": {
                "emotions": emotionsResult.emotions,
                "primary_emotion": emotionsResult.emotions[0] if emotionsResult.emotions else None,
                "intent": intentAndNeedsResult.get("intent"),
                "psychological_need": intentAndNeedsResult.get("psychological_need")
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in chat_final: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)