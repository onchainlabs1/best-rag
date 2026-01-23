"""Test Specs for health API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.v1.health import router
from src.config import settings
from src.shared_services import agent_service


@pytest.fixture
def client() -> TestClient:
    """Fixture: FastAPI test client."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Spec: GET /health should return health status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_debug_info_enabled(client: TestClient) -> None:
    """Spec: GET /health/debug should return debug info when DEBUG=true."""
    with patch.object(settings, "debug", True):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_retriever = MagicMock()
        mock_retriever.collection = mock_collection
        mock_retriever.collection_name = "test_collection"
        mock_retriever.client._settings.path = "/test/path"
        mock_retriever.retrieve.return_value = MagicMock(chunks=[MagicMock()])

        with patch.object(agent_service, "retriever", mock_retriever):
            response = client.get("/health/debug")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["collection_count"] == 10
            assert "collection_name" in data


def test_debug_info_disabled(client: TestClient) -> None:
    """Spec: GET /health/debug should return 403 when DEBUG=false."""
    with patch.object(settings, "debug", False):
        response = client.get("/health/debug")
        assert response.status_code == 403
        assert "Debug endpoint is only available" in response.json()["detail"]


def test_debug_info_error(client: TestClient) -> None:
    """Spec: GET /health/debug should handle errors gracefully."""
    with patch.object(settings, "debug", True):
        with patch.object(agent_service.retriever.collection, "count", side_effect=Exception("Error")):
            response = client.get("/health/debug")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "error" in data
