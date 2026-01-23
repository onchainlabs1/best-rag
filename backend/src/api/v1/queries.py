"""Query endpoints."""

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter

from src.config import settings
from src.schemas.api import QueryRequest, QueryResponse
from src.shared_services import agent_service

router = APIRouter(prefix="/queries", tags=["queries"])

# Rate limiter - will be set from app state
limiter: Limiter | None = None


@router.post("", response_model=QueryResponse)
async def process_query(request: Request, query_request: QueryRequest) -> QueryResponse:
    """
    Process a query and return an answer.

    Args:
        request: FastAPI request (for rate limiting)
        query_request: Query request

    Returns:
        Query response with answer and sources
    """
    # Apply rate limiting if enabled
    if settings.rate_limit_enabled and limiter:
        # Use limiter from app state
        app_limiter = request.app.state.limiter
        app_limiter.limit(settings.rate_limit_queries)(lambda: None)()

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
                    metadata={
                        "error": "no_documents",
                        "message": "No documents have been indexed yet",
                    },
                )
        except Exception:
            # If we can't check, try to process anyway
            pass

        response = agent_service.process_query(query_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}",
        ) from e
