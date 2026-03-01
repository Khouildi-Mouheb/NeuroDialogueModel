import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from presentation.modelFactory import ModelFactory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI(
    title="Neurodialogue Model API",
    description="Intelligent emotional support chatbot powered by RAG and agentic verification",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


chat_orchestrator      = None
embedding_orchestrator = None

@app.on_event("startup")
async def startup():
    global chat_orchestrator, embedding_orchestrator

    logger.info("  [Startup] Building ChatOrchestrator...")
    chat_orchestrator = ModelFactory.buildChatOrchestrator()

    logger.info("  [Startup] Building EmbeddingOrchestrator...")
    embedding_orchestrator = ModelFactory.buildEmbeddingOrchestrator()

    logger.info("  [Startup] Ready ✓")


@app.post("/")
async def chat(request: Request):
    from presentation.routers.chatRouter import ChatRequest, chat as chat_handler
    body = await request.json()
    chat_request = ChatRequest(**body)
    return await chat_handler(chat_request, orchestrator=chat_orchestrator)


@app.post("/index/")
async def index(request: Request):
    print('start indexing')
    from presentation.routers.embeddingRouter import IndexRequest, index as index_handler
    body = await request.json()
    req = IndexRequest(**body)
    return index_handler(req, orchestrator=embedding_orchestrator)


@app.delete("/document/")
async def delete(request: Request):
    from presentation.routers.embeddingRouter import DeleteRequest, delete as delete_handler
    body = await request.json()
    req = DeleteRequest(**body)
    return delete_handler(req, orchestrator=embedding_orchestrator)



@app.get("/health/")
def health():
    return {
        "status": "ok",
        "model": "neurodialogue-v1.0",
        "chat_ready":      chat_orchestrator is not None,
        "embedding_ready": embedding_orchestrator is not None,
    }