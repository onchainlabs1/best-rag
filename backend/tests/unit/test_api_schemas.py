"""Test Specs for API schemas."""

from datetime import datetime

from src.schemas.api import (
    DocumentInfo,
    DocumentUpload,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    SourceInfo,
)


def test_document_upload() -> None:
    """Spec: DocumentUpload should accept file content."""
    upload = DocumentUpload(
        filename="test.txt",
        content="File content here",
        content_type="text/plain",
        metadata={"author": "test"},
    )
    assert upload.filename == "test.txt"
    assert upload.content == "File content here"
    assert upload.content_type == "text/plain"
    assert upload.metadata == {"author": "test"}


def test_document_info() -> None:
    """Spec: DocumentInfo should contain document metadata."""
    doc = DocumentInfo(
        id="doc_1",
        filename="test.txt",
        content_type="text/plain",
        uploaded_at=datetime.now(),
        chunk_count=5,
        metadata={},
    )
    assert doc.id == "doc_1"
    assert doc.filename == "test.txt"
    assert doc.chunk_count == 5


def test_query_request() -> None:
    """Spec: QueryRequest should validate query length and parameters."""
    request = QueryRequest(
        query="What is Python?",
        top_k=5,
        score_threshold=0.7,
        stream=False,
    )
    assert request.query == "What is Python?"
    assert request.top_k == 5
    assert request.score_threshold == 0.7


def test_query_request_validation() -> None:
    """Spec: QueryRequest should validate top_k and score_threshold ranges."""
    # Valid ranges
    request1 = QueryRequest(query="test", top_k=1)
    assert request1.top_k == 1

    request2 = QueryRequest(query="test", top_k=20)
    assert request2.top_k == 20

    request3 = QueryRequest(query="test", score_threshold=0.0)
    assert request3.score_threshold == 0.0

    request4 = QueryRequest(query="test", score_threshold=1.0)
    assert request4.score_threshold == 1.0


def test_query_response() -> None:
    """Spec: QueryResponse should contain answer and sources."""
    response = QueryResponse(
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
    assert response.answer == "Python is a programming language."
    assert len(response.sources) == 1
    assert response.score == 0.9


def test_health_response() -> None:
    """Spec: HealthResponse should indicate service status."""
    health = HealthResponse(
        status="healthy",
        version="0.1.0",
    )
    assert health.status == "healthy"
    assert health.version == "0.1.0"
    assert isinstance(health.timestamp, datetime)
