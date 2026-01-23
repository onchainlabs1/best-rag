"""Health check endpoint."""

from fastapi import APIRouter, HTTPException, status

from src import __version__
from src.config import settings
from src.schemas.api import HealthResponse
from src.shared_services import agent_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
    )


@router.get("/debug")
async def debug_info() -> dict:
    """
    Debug endpoint to check ChromaDB status.

    Only available when DEBUG mode is enabled for security.

    Returns:
        Debug information about the knowledge base

    Raises:
        HTTPException: If debug mode is not enabled
    """
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoint is only available when DEBUG mode is enabled",
        )

    try:
        collection_count = agent_service.retriever.collection.count()

        # Try a simple search
        test_result = agent_service.retriever.retrieve("test", top_k=1, score_threshold=0.0)

        return {
            "status": "ok",
            "chromadb_count": collection_count,
            "test_query_results": len(test_result.chunks),
            "collection_name": agent_service.retriever.collection_name,
            "chroma_path": agent_service.retriever.client._settings.path
            if hasattr(agent_service.retriever.client, "_settings")
            else "unknown",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
