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
from infrastructure.agents.smartIntentNeedsAgent import SmartIntentNeedsAgent

# Create FastAPI app
app = FastAPI(
    title="NeuroDialogue Model API",
    description="API for RAG-based chat model with emotion detection and intent analysis",
    version="2.0.0"
)

# CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents (singleton pattern - create once)
emotion_agent = EmotionDetectionAgent()
intent_agent = SmartIntentNeedsAgent()
generator = CloudBasedGenerator()

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the chat HTML interface"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "chat.html")
        
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>NeuroDialogue API</title></head>
                <body style="font-family: Arial; padding: 40px; text-align: center;">
                    <h1>🤖 NeuroDialogue Model API</h1>
                    <p>Chat interface not found. Use the API endpoints instead:</p>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 10px;"><a href="/health">/health</a> - Health check</li>
                        <li style="margin: 10px;"><a href="/api-info">/api-info</a> - API information</li>
                        <li style="margin: 10px;">/chat?text=your_message - Streaming chat</li>
                        <li style="margin: 10px;">/chat_final?text=your_message - Complete chat response</li>
                        <li style="margin: 10px;">/analyze?text=your_message - Emotion & intent analysis</li>
                    </ul>
                </body>
            </html>
            """,
            status_code=200
        )

@app.get("/api-info")
def api_info():
    """Return API information as JSON"""
    return {
        "message": "NeuroDialogue Model API",
        "version": "2.0.0",
        "features": [
            "Emotion Detection (27 emotions)",
            "Intent & Needs Analysis",
            "RAG-based Response Generation",
            "Streaming Support"
        ],
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_info": "/api-info",
            "chat_streaming": "/chat?text=your_message",
            "chat_complete": "/chat_final?text=your_message",
            "analyze": "/analyze?text=your_message"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "neurodialogue-model", "version": "2.0.0"}

@app.get("/analyze")
def analyze_message(text: str = Query(..., min_length=1, max_length=2000)):
    """Analyze emotions and intent without generating a response"""
    try:
        # Create user query
        query = UserQuery(text=text)
        
        # Detect emotions
        emotion_result = emotion_agent.detect_emotions(query, top_k=3)
        
        # Analyze intent and needs
        intent_analysis = intent_agent.analyze(text)
        
        return {
            "query": text,
            "emotions": {
                "top_emotions": emotion_result.emotions,
                "scores": emotion_result.emotionsWithScore,
                "primary_emotion": emotion_result.emotions[0] if emotion_result.emotions else None
            },
            "intent": intent_analysis["intent"],
            "psychological_need": intent_analysis["psychological_need"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}")
        return {"error": str(e), "status": "failed"}

@app.get("/chat_final")
def chat_final(text: str = Query(..., min_length=1, max_length=2000)):
    """Complete chat response with emotion detection"""
    try:
        # Create user query
        query = UserQuery(text=text)
        
        # Detect emotions
        emotion_result = emotion_agent.detect_emotions(query, top_k=3)
        
        # Analyze intent
        intent_analysis = intent_agent.analyze(text)
        
        # Create user state with emotions
        user_state = UserState(emotions=emotion_result)
        
        # Create generator context
        generator_context = GeneratorContext(
            user_query=query,
            user_state=user_state
        )
        
        # Generate response
        full_response = ""
        prompt = generator_context.format_context_for_prompt()
        for token in generator.stream(prompt):
            full_response += token
        
        return {
            "response": full_response,
            "query": text,
            "analysis": {
                "emotions": emotion_result.emotions,
                "primary_emotion": emotion_result.emotions[0] if emotion_result.emotions else None,
                "intent": intent_analysis["intent"],
                "psychological_need": intent_analysis["psychological_need"]
            },
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@app.get("/chat")
def chat_stream(text: str = Query(..., min_length=1, max_length=2000)):
    """Streaming chat with emotion-aware responses"""
    def event_generator():
        try:
            # Create user query
            query = UserQuery(text=text)
            
            # Detect emotions (runs in background while streaming)
            emotion_result = emotion_agent.detect_emotions(query, top_k=3)
            
            # Analyze intent
            intent_analysis = intent_agent.analyze(text)
            
            # Send analysis first (optional - can be removed if you don't want this)
            yield f"data: [ANALYSIS] Emotion: {emotion_result.emotions[0] if emotion_result.emotions else 'neutral'}, Intent: {intent_analysis['intent']}\n\n"
            
            # Create user state
            user_state = UserState(emotions=emotion_result)
            
            # Create generator context
            generator_context = GeneratorContext(
                user_query=query,
                user_state=user_state
            )
            
            # Stream response
            prompt = generator_context.format_context_for_prompt()
            for token in generator.stream(prompt):
                yield f"data: {token}\n\n"
                
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

