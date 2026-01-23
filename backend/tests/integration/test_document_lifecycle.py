"""Integration tests for document lifecycle: upload → query → delete."""

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


def test_document_upload_and_list(document_service: DocumentService) -> None:
    """Spec: Upload document and list it."""
    upload = DocumentUpload(
        filename="test.txt",
        content="This is a test document with some content.",
        content_type="text/plain",
    )

    doc = document_service.upload_document(upload)
    assert doc.id is not None
    assert doc.filename == "test.txt"
    assert doc.chunk_count > 0

    # List documents
    docs = document_service.list_documents()
    assert len(docs) == 1
    assert docs[0].id == doc.id


def test_document_persistence_after_restart(document_service: DocumentService) -> None:
    """Spec: Documents persist after service restart (simulated)."""
    upload = DocumentUpload(
        filename="persistent.txt",
        content="This document should persist.",
        content_type="text/plain",
    )

    doc = document_service.upload_document(upload)
    doc_id = doc.id

    # Simulate restart: create new service instance with same storage

    temp_data_dir = Path(document_service.storage.db_path).parent

    embedding_service = EmbeddingService(provider="local", model="all-MiniLM-L6-v2")
    retriever = RAGRetriever(
        collection_name="test_collection",
        embedding_service=embedding_service,
    )
    storage = DocumentStorage(db_path=str(temp_data_dir / "documents.db"))

    new_service = DocumentService(
        retriever=retriever,
        storage=storage,
    )

    # Document should still be available
    retrieved_doc = new_service.get_document(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.filename == "persistent.txt"

    docs = new_service.list_documents()
    assert len(docs) == 1
    assert docs[0].id == doc_id


def test_document_query_after_upload(document_service: DocumentService) -> None:
    """Spec: Query should find uploaded document."""
    upload = DocumentUpload(
        filename="query_test.txt",
        content="The capital of France is Paris. Paris is a beautiful city.",
        content_type="text/plain",
    )

    document_service.upload_document(upload)

    # Query for the document
    retriever = document_service.retriever
    result = retriever.retrieve("What is the capital of France?", top_k=5, score_threshold=0.0)

    assert len(result.chunks) > 0
    # Check that at least one chunk contains relevant content
    found_relevant = any("Paris" in chunk.content for chunk in result.chunks)
    assert found_relevant


def test_document_delete(document_service: DocumentService) -> None:
    """Spec: Delete document removes it from storage and ChromaDB."""
    upload = DocumentUpload(
        filename="to_delete.txt",
        content="This document will be deleted.",
        content_type="text/plain",
    )

    doc = document_service.upload_document(upload)
    doc_id = doc.id

    # Verify it exists
    assert document_service.get_document(doc_id) is not None

    # Delete it
    deleted = document_service.delete_document(doc_id)
    assert deleted is True

    # Verify it's gone
    assert document_service.get_document(doc_id) is None
    docs = document_service.list_documents()
    assert len(docs) == 0


def test_score_threshold_enforcement(document_service: DocumentService) -> None:
    """Spec: score_threshold should be strictly enforced (no fallback)."""
    upload = DocumentUpload(
        filename="threshold_test.txt",
        content="This is a completely unrelated document about nothing important.",
        content_type="text/plain",
    )

    document_service.upload_document(upload)

    # Query with very high threshold - should return empty if no match
    retriever = document_service.retriever
    result = retriever.retrieve(
        "completely different topic that won't match",
        top_k=10,
        score_threshold=0.95,  # Very high threshold
    )

    # All returned results must meet the threshold
    if len(result.chunks) > 0:
        assert all(score >= 0.95 for score in result.scores)
    # It's acceptable to return empty if nothing matches
