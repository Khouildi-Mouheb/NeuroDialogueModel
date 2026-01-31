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

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the chat HTML interface"""
    try:
        # Get the directory where chat.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "chat.html")
        
        # Read and return the HTML file
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback if chat.html is not found
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
        "version": "1.0.0",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_info": "/api-info",
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