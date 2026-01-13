"""Test Specs for document chunking."""

import pytest
from src.rag.chunking import DocumentChunker
from src.schemas.rag import DocumentChunk


def test_chunker_initialization() -> None:
    """Spec: DocumentChunker should initialize with default parameters."""
    chunker = DocumentChunker()
    assert chunker.splitter._chunk_size == 1000
    assert chunker.splitter._chunk_overlap == 200


def test_chunker_custom_parameters() -> None:
    """Spec: DocumentChunker should accept custom chunk size and overlap."""
    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
    assert chunker.splitter._chunk_size == 500
    assert chunker.splitter._chunk_overlap == 100


def test_chunk_document() -> None:
    """Spec: chunk_document should split text into chunks."""
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    content = "This is a test document. " * 10  # ~300 chars
    chunks = chunker.chunk_document(content, source="test.txt")

    assert len(chunks) > 1
    assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
    assert all(chunk.source == "test.txt" for chunk in chunks)


def test_chunk_document_metadata() -> None:
    """Spec: chunk_document should preserve metadata."""
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    content = "Test content here."
    metadata = {"author": "test", "type": "article"}
    chunks = chunker.chunk_document(content, source="test.txt", metadata=metadata)

    assert len(chunks) >= 1
    assert all("author" in chunk.metadata for chunk in chunks)
    assert all("type" in chunk.metadata for chunk in chunks)
    assert all(chunk.metadata["author"] == "test" for chunk in chunks)


def test_chunk_document_ids() -> None:
    """Spec: chunk_document should generate unique chunk IDs."""
    chunker = DocumentChunker(chunk_size=100)
    content = "Test content " * 20
    chunks = chunker.chunk_document(content, source="test.txt")

    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))  # All unique
    assert all(chunk_id is not None for chunk_id in chunk_ids)


def test_chunk_documents_multiple() -> None:
    """Spec: chunk_documents should handle multiple documents."""
    chunker = DocumentChunker(chunk_size=50)
    documents = [
        {"content": "First document content.", "source": "doc1.txt"},
        {"content": "Second document content.", "source": "doc2.txt"},
    ]
    chunks = chunker.chunk_documents(documents)

    assert len(chunks) >= 2
    sources = {chunk.source for chunk in chunks}
    assert "doc1.txt" in sources
    assert "doc2.txt" in sources
