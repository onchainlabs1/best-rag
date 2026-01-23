"""Test Specs for document API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.v1.documents import router
from src.schemas.api import DocumentInfo, DocumentUpload
from src.shared_services import document_service


@pytest.fixture
def client() -> TestClient:
    """Fixture: FastAPI test client."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_upload() -> DocumentUpload:
    """Fixture: Sample document upload."""
    return DocumentUpload(
        filename="test.txt",
        content="This is test content.",
        content_type="text/plain",
    )


@pytest.fixture
def sample_doc_info() -> DocumentInfo:
    """Fixture: Sample document info."""
    from datetime import datetime
    return DocumentInfo(
        id="test_doc_1",
        filename="test.txt",
        content_type="text/plain",
        uploaded_at=datetime.now(),
        chunk_count=1,
        metadata={},
    )


def test_upload_document_success(client: TestClient, sample_upload: DocumentUpload, sample_doc_info: DocumentInfo) -> None:
    """Spec: POST /documents should upload a document successfully."""
    with patch.object(document_service, "upload_document", return_value=sample_doc_info):
        response = client.post("/documents", json=sample_upload.model_dump())
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test_doc_1"
        assert data["filename"] == "test.txt"
        assert data["chunk_count"] == 1


def test_upload_document_error(client: TestClient, sample_upload: DocumentUpload) -> None:
    """Spec: POST /documents should return 500 on service error."""
    with patch.object(document_service, "upload_document", side_effect=Exception("Upload failed")):
        response = client.post("/documents", json=sample_upload.model_dump())
        assert response.status_code == 500
        assert "Failed to upload document" in response.json()["detail"]


def test_list_documents(client: TestClient, sample_doc_info: DocumentInfo) -> None:
    """Spec: GET /documents should return list of documents."""
    with patch.object(document_service, "list_documents", return_value=[sample_doc_info]):
        response = client.get("/documents")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["documents"]) == 1
        assert data["documents"][0]["id"] == "test_doc_1"


def test_get_document_success(client: TestClient, sample_doc_info: DocumentInfo) -> None:
    """Spec: GET /documents/{doc_id} should return document info."""
    with patch.object(document_service, "get_document", return_value=sample_doc_info):
        response = client.get("/documents/test_doc_1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_doc_1"
        assert data["filename"] == "test.txt"


def test_get_document_not_found(client: TestClient) -> None:
    """Spec: GET /documents/{doc_id} should return 404 for non-existent document."""
    with patch.object(document_service, "get_document", return_value=None):
        response = client.get("/documents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_delete_document_success(client: TestClient) -> None:
    """Spec: DELETE /documents/{doc_id} should delete document."""
    with patch.object(document_service, "delete_document", return_value=True):
        response = client.delete("/documents/test_doc_1")
        assert response.status_code == 204


def test_delete_document_not_found(client: TestClient) -> None:
    """Spec: DELETE /documents/{doc_id} should return 404 for non-existent document."""
    with patch.object(document_service, "delete_document", return_value=False):
        response = client.delete("/documents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_upload_documents_batch(client: TestClient, sample_upload: DocumentUpload, sample_doc_info: DocumentInfo) -> None:
    """Spec: POST /documents/batch should upload multiple documents."""
    from src.schemas.api import BatchDocumentUpload

    batch = BatchDocumentUpload(documents=[sample_upload, sample_upload])

    with patch.object(document_service, "upload_document", return_value=sample_doc_info):
        response = client.post("/documents/batch", json=batch.model_dump())
        assert response.status_code == 201
        data = response.json()
        assert data["total"] == 2
        assert data["success_count"] == 2
        assert len(data["documents"]) == 2


def test_upload_documents_batch_partial_failure(client: TestClient, sample_upload: DocumentUpload, sample_doc_info: DocumentInfo) -> None:
    """Spec: POST /documents/batch should handle partial failures."""
    from src.schemas.api import BatchDocumentUpload

    batch = BatchDocumentUpload(documents=[sample_upload, sample_upload])

    def mock_upload(upload: DocumentUpload) -> DocumentInfo:
        if upload.filename == "test.txt":
            return sample_doc_info
        raise Exception("Upload failed")

    with patch.object(document_service, "upload_document", side_effect=mock_upload):
        response = client.post("/documents/batch", json=batch.model_dump())
        assert response.status_code == 201
        data = response.json()
        assert data["total"] == 2
        assert data["success_count"] == 1
        assert data["error_count"] == 1
        assert len(data["errors"]) == 1
