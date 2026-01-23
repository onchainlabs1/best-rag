"""Agent chat endpoints with streaming."""

import json
from collections.abc import Iterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter

from src.config import settings
from src.schemas.api import QueryRequest
from src.shared_services import agent_service

router = APIRouter(prefix="/agents/chat", tags=["agents"])

# Rate limiter - will be set from app state
limiter: Limiter | None = None


@router.post("", response_class=StreamingResponse)
async def chat_stream(request: Request, query_request: QueryRequest) -> StreamingResponse:
    """
    Chat with agent using streaming responses (SSE).

    Args:
        request: Query request

    Returns:
        Streaming response with agent updates
    """
    # Apply rate limiting if enabled
    if settings.rate_limit_enabled:
        app_limiter = request.app.state.limiter
        app_limiter.limit(settings.rate_limit_agents)(lambda: None)()

    def generate() -> Iterator[str]:
        """Generate SSE events from agent stream."""
        try:
            for state_update in agent_service.process_query_stream(query_request):
                # Format as SSE event
                data = json.dumps(state_update)
                yield f"data: {data}\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
