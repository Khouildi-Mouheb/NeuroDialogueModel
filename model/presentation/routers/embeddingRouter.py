from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()


class IndexRequest(BaseModel):
    pdf_path: str                    

class IndexResponse(BaseModel):
    status: str
    pdf_path: str
    chunks_indexed: int
    error: Optional[str] = None

class DeleteRequest(BaseModel):
    document_id: str

class DeleteResponse(BaseModel):
    status: str
    document_id: str
    chunks_deleted: int
    error: Optional[str] = None



@router.post("/index/", response_model=IndexResponse)
def index(request: IndexRequest, orchestrator=None):
    """
    Receive PDF path from Django.
    Run full pipeline: Load → Preprocess → Chunk → Embed → Index.
    ChromaDB saves the vectors.
    Return chunk count to Django.
    """
    logger.info(f"  [EmbeddingRouter] Indexing: {request.pdf_path}")

    if not os.path.exists(request.pdf_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {request.pdf_path}"
        )

    if not request.pdf_path.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        chunks_indexed = orchestrator.indexDocument(request.pdf_path)

        logger.info(f"  [EmbeddingRouter] Done — {chunks_indexed} chunks indexed")

        return IndexResponse(
            status="success",
            pdf_path=request.pdf_path,
            chunks_indexed=chunks_indexed,
            error=None,
        )

    except Exception as e:
        logger.error(f"  [EmbeddingRouter] Error: {str(e)}", exc_info=True)
        return IndexResponse(
            status="error",
            pdf_path=request.pdf_path,
            chunks_indexed=0,
            error=str(e),
        )


@router.delete("/document/", response_model=DeleteResponse)
def delete(request: DeleteRequest, orchestrator=None):
    """
    Delete all chunks belonging to a document from ChromaDB.
    """
    logger.info(f"  [EmbeddingRouter] Deleting document: {request.document_id}")

    try:
        chunks_deleted = orchestrator.deleteDocument(request.document_id)

        logger.info(f"  [EmbeddingRouter] Deleted {chunks_deleted} chunks")

        return DeleteResponse(
            status="success",
            document_id=request.document_id,
            chunks_deleted=chunks_deleted,
            error=None,
        )

    except Exception as e:
        logger.error(f"  [EmbeddingRouter] Error: {str(e)}", exc_info=True)
        return DeleteResponse(
            status="error",
            document_id=request.document_id,
            chunks_deleted=0,
            error=str(e),
        )