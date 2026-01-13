"""Agent chat endpoints with streaming."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Iterator
import json
from src.schemas.api import QueryRequest
from src.shared_services import agent_service

router = APIRouter(prefix="/agents/chat", tags=["agents"])


@router.post("", response_class=StreamingResponse)
async def chat_stream(request: QueryRequest) -> StreamingResponse:
    """
    Chat with agent using streaming responses (SSE).

    Args:
        request: Query request

    Returns:
        Streaming response with agent updates
    """

    def generate() -> Iterator[str]:
        """Generate SSE events from agent stream."""
        try:
            for state_update in agent_service.process_query_stream(request):
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
