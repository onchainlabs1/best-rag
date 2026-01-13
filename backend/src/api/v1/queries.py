"""Query endpoints."""

from fastapi import APIRouter, HTTPException, status
from src.schemas.api import QueryRequest, QueryResponse
from src.shared_services import agent_service, document_service

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Process a query and return an answer.

    Args:
        request: Query request

    Returns:
        Query response with answer and sources
    """
    try:
        # Check directly in ChromaDB if there are indexed documents
        # This is more reliable than checking DocumentService (which uses memory)
        try:
            collection_count = agent_service.retriever.collection.count()
            if collection_count == 0:
                return QueryResponse(
                    answer="No documents are indexed in the knowledge base. Please upload at least one document before making queries.",
                    sources=[],
                    score=0.0,
                    metadata={"error": "no_documents", "message": "No documents have been indexed yet"}
                )
        except Exception:
            # If we can't check, try to process anyway
            pass
        
        response = agent_service.process_query(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}",
        ) from e
