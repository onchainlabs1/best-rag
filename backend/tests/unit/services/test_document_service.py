"""Test Specs for DocumentService."""

import shutil
import tempfile
from pathlib import Path

import pytest

import src.config
from src.rag.embeddings import EmbeddingService
from src.rag.retriever import RAGRetriever
from src.schemas.api import DocumentUpload
from src.services.document_service import DocumentService
from src.services.document_storage import DocumentStorage


@pytest.fixture
def temp_data_dir() -> str:
    """Fixture: Temporary directory for data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def document_service(temp_data_dir: str) -> DocumentService:
    """Fixture: Document service with temporary storage."""
    original_chroma_path = src.config.settings.chroma_path
    src.config.settings.chroma_path = str(Path(temp_data_dir) / "chroma")

    embedding_service = EmbeddingService(provider="local", model="all-MiniLM-L6-v2")
    retriever = RAGRetriever(
        collection_name="test_collection",
        embedding_service=embedding_service,
    )
    storage = DocumentStorage(db_path=str(Path(temp_data_dir) / "documents.db"))

    service = DocumentService(
        retriever=retriever,
        storage=storage,
    )

    yield service

    retriever.delete_collection()
    src.config.settings.chroma_path = original_chroma_path


def test_upload_document_success(document_service: DocumentService) -> None:
    """Spec: upload_document should process and store document."""
    upload = DocumentUpload(
        filename="test.txt",
        content="This is test content for the document.",
        content_type="text/plain",
    )

    doc = document_service.upload_document(upload)

    assert doc.id is not None
    assert doc.filename == "test.txt"
    assert doc.chunk_count > 0
    assert doc.content_type == "text/plain"


def test_upload_document_with_metadata(document_service: DocumentService) -> None:
    """Spec: upload_document should preserve metadata."""
    upload = DocumentUpload(
        filename="test.txt",
        content="Test content",
        content_type="text/plain",
        metadata={"author": "Test Author", "category": "test"},
    )

    doc = document_service.upload_document(upload)

    assert doc.metadata == {"author": "Test Author", "category": "test"}


def test_list_documents(document_service: DocumentService) -> None:
    """Spec: list_documents should return all uploaded documents."""
    upload1 = DocumentUpload(
        filename="test1.txt",
        content="Content 1",
        content_type="text/plain",
    )
    upload2 = DocumentUpload(
        filename="test2.txt",
        content="Content 2",
        content_type="text/plain",
    )

    document_service.upload_document(upload1)
    document_service.upload_document(upload2)

    docs = document_service.list_documents()
    assert len(docs) == 2
    assert {doc.filename for doc in docs} == {"test1.txt", "test2.txt"}


def test_get_document(document_service: DocumentService) -> None:
    """Spec: get_document should return document by ID."""
    upload = DocumentUpload(
        filename="test.txt",
        content="Test content",
        content_type="text/plain",
    )

    doc = document_service.upload_document(upload)
    retrieved = document_service.get_document(doc.id)

    assert retrieved is not None
    assert retrieved.id == doc.id
    assert retrieved.filename == "test.txt"


def test_get_document_not_found(document_service: DocumentService) -> None:
    """Spec: get_document should return None for non-existent document."""
    result = document_service.get_document("nonexistent_id")
    assert result is None


def test_delete_document(document_service: DocumentService) -> None:
    """Spec: delete_document should remove document and chunks."""
    upload = DocumentUpload(
        filename="test.txt",
        content="Test content",
        content_type="text/plain",
    )

    doc = document_service.upload_document(upload)
    deleted = document_service.delete_document(doc.id)

    assert deleted is True
    assert document_service.get_document(doc.id) is None


def test_delete_document_not_found(document_service: DocumentService) -> None:
    """Spec: delete_document should return False for non-existent document."""
    deleted = document_service.delete_document("nonexistent_id")
    assert deleted is False


def test_upload_document_empty_content(document_service: DocumentService) -> None:
    """Spec: upload_document should handle empty content gracefully."""
    upload = DocumentUpload(
        filename="empty.txt",
        content="",
        content_type="text/plain",
    )

    # Should not raise exception, but may have 0 chunks
    doc = document_service.upload_document(upload)
    assert doc.id is not None
    # Empty content might result in 0 chunks
    assert doc.chunk_count >= 0
