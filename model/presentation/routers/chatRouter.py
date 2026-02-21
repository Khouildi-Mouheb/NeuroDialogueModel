from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()




class ChatRequest(BaseModel):
    text: str                        

class ChatResponse(BaseModel):
    status: str                      
    data: str                        
    error: Optional[str] = None
    analysis: Optional[dict] = None  



@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, orchestrator=None):
    """
    Receive user message from Django, run full pipeline,
    return reply in the format Django expects.
    """
    logger.info(f"  [ChatRouter] Received: \"{request.text}\"")

    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    try:
        reply, aggregated = orchestrator.handleUserMessageWithVerification(
            request.text,
            top_k=5,
        )

        analysis = {}
        if aggregated:
            analysis = {
                "verification_status": aggregated.status.value,
                "scores": aggregated.all_scores,
                "issues": [i.value for i in aggregated.all_issues],
            }

        logger.info(f"  [ChatRouter] Reply: \"{reply[:80]}...\"")

        return ChatResponse(
            status="success",
            data=reply,
            error=None,
            analysis=analysis,
        )

    except Exception as e:
        logger.error(f"  [ChatRouter] Error: {str(e)}", exc_info=True)
        return ChatResponse(
            status="error",
            data="",
            error=str(e),
        )