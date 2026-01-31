import sys
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.domain.userQuery import UserQuery
from core.context.generatorContext import GeneratorContext
from infrastructure.agents.generatorAgent import GeneratorAgent

# Create FastAPI app
app = FastAPI(
    title="NeuroDialogue Model API",
    description="API for RAG-based chat model",
    version="1.0.0"
)

# CORS - Allow all origins (you can restrict this later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "NeuroDialogue Model API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat_streaming": "/chat?text=your_message",
            "chat_complete": "/chat_final?text=your_message"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "neurodialogue-model"}

@app.get("/chat_final")
def chat_final(text: str = Query(..., min_length=1, max_length=2000)):
    try:
        query = UserQuery(text=text)
        generator_context = GeneratorContext(user_query=query)
        generator = GeneratorAgent()
        
        full_response = ""
        for token in generator.stream(generator_context):
            full_response += token
        
        return {
            "response": full_response,
            "query": text,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@app.get("/chat")
def chat_stream(text: str = Query(..., min_length=1, max_length=2000)):
    def event_generator():
        try:
            query = UserQuery(text=text)
            generator_context = GeneratorContext(user_query=query)
            generator = GeneratorAgent()
            
            for token in generator.stream(generator_context):
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)