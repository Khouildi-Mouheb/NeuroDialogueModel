# app/chat.py
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse

# Fix paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.domain.userQuery import UserQuery
from core.context.retrieverContext import RetieverContext
from core.context.generatorContext import GeneratorContext
from core.domain.userState import UserState

from infrastructure.agents.emotionDetectionAgent import EmotionDetectionAgent
from infrastructure.rerieval.chromadbVectorStore import ChromaDBVectorStore
from infrastructure.agents.generatorAgent import GeneratorAgent


app = FastAPI(title="RAG System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




# Add this route
@app.get("/")
def read_root():
    return FileResponse('chat.html')

@app.get("/chat_final")
def chat_final(text: str):
    query = UserQuery(text=text)
    generator_context = GeneratorContext(user_query=query)
    generator = GeneratorAgent()

    full_response = ""
    for token in generator.stream(generator_context):
        full_response += token

    return {"response": full_response}



@app.get("/chat")
def chat_stream(text: str):

    def event_generator():
        query = UserQuery(text=text)

        generator_context = GeneratorContext(
            user_query=query,
        )
        generator = GeneratorAgent()

        for token in generator.stream(generator_context):
            yield f"data: {token}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
