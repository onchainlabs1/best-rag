"""Test Specs for agent API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.v1.agents import router
from src.schemas.api import QueryRequest
from src.shared_services import agent_service


@pytest.fixture
def client() -> TestClient:
    """Fixture: FastAPI test client."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_query_request() -> QueryRequest:
    """Fixture: Sample query request."""
    return QueryRequest(
        query="What is Python?",
        top_k=5,
        score_threshold=0.7,
        stream=True,
    )


def test_chat_stream_success(client: TestClient, sample_query_request: QueryRequest) -> None:
    """Spec: POST /agents/chat should stream agent responses."""
    mock_stream = [
        {"node": "retrieve", "state": {"query": "What is Python?"}},
        {"node": "generate", "state": {"response": "Python is..."}},
        {"node": "finalize", "state": {"response": "Python is a programming language."}},
    ]

    with patch.object(agent_service, "process_query_stream", return_value=iter(mock_stream)):
        response = client.post("/agents/chat", json=sample_query_request.model_dump())
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Parse SSE events
        lines = response.text.strip().split("\n")
        data_lines = [line for line in lines if line.startswith("data: ")]

        # Should have 3 data events + 1 DONE event
        assert len(data_lines) >= 3
        assert any("DONE" in line for line in data_lines)


def test_chat_stream_error(client: TestClient, sample_query_request: QueryRequest) -> None:
    """Spec: POST /agents/chat should handle errors in stream."""
    with patch.object(agent_service, "process_query_stream", side_effect=Exception("Stream error")):
        response = client.post("/agents/chat", json=sample_query_request.model_dump())
        assert response.status_code == 200
        assert "error" in response.text.lower()


def test_chat_stream_empty(client: TestClient, sample_query_request: QueryRequest) -> None:
    """Spec: POST /agents/chat should handle empty stream."""
    with patch.object(agent_service, "process_query_stream", return_value=iter([])):
        response = client.post("/agents/chat", json=sample_query_request.model_dump())
        assert response.status_code == 200
        # Should still have DONE event
        assert "DONE" in response.text
