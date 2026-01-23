"""Test Specs for query API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.v1.queries import router
from src.schemas.api import QueryRequest, QueryResponse, SourceInfo
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
    )


@pytest.fixture
def sample_query_response() -> QueryResponse:
    """Fixture: Sample query response."""
    return QueryResponse(
        answer="Python is a programming language.",
        sources=[
            SourceInfo(
                chunk_id="chunk_1",
                content="Python is...",
                source="doc1",
                score=0.9,
            ),
        ],
        score=0.9,
    )


def test_process_query_success(client: TestClient, sample_query_request: QueryRequest, sample_query_response: QueryResponse) -> None:
    """Spec: POST /queries should process query successfully."""
    with patch.object(agent_service, "process_query", return_value=sample_query_response):
        with patch.object(agent_service.retriever.collection, "count", return_value=10):
            response = client.post("/queries", json=sample_query_request.model_dump())
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "Python is a programming language."
            assert len(data["sources"]) == 1
            assert data["score"] == 0.9


def test_process_query_no_documents(client: TestClient, sample_query_request: QueryRequest) -> None:
    """Spec: POST /queries should return message when no documents indexed."""
    with patch.object(agent_service.retriever.collection, "count", return_value=0):
        response = client.post("/queries", json=sample_query_request.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "No documents are indexed" in data["answer"]
        assert data["score"] == 0.0
        assert data["metadata"]["error"] == "no_documents"


def test_process_query_error(client: TestClient, sample_query_request: QueryRequest) -> None:
    """Spec: POST /queries should return 500 on service error."""
    with patch.object(agent_service, "process_query", side_effect=Exception("Query failed")):
        with patch.object(agent_service.retriever.collection, "count", return_value=10):
            response = client.post("/queries", json=sample_query_request.model_dump())
            assert response.status_code == 500
            assert "Failed to process query" in response.json()["detail"]


def test_process_query_with_collection_error(client: TestClient, sample_query_request: QueryRequest, sample_query_response: QueryResponse) -> None:
    """Spec: POST /queries should continue even if collection count fails."""
    with patch.object(agent_service, "process_query", return_value=sample_query_response):
        with patch.object(agent_service.retriever.collection, "count", side_effect=Exception("Count failed")):
            response = client.post("/queries", json=sample_query_request.model_dump())
            # Should still process query even if count check fails
            assert response.status_code == 200
