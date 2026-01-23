"""Test Specs for RAG schemas."""

import pytest

from src.schemas.rag import DocumentChunk, EmbeddingRequest, EmbeddingResponse, RetrievalResult


def test_document_chunk_creation(sample_chunk: DocumentChunk) -> None:
    """Spec: DocumentChunk should be created with required fields."""
    assert sample_chunk.content == "This is a sample document chunk for testing."
    assert sample_chunk.metadata == {"source": "test_doc.txt", "position": 0}
    assert sample_chunk.chunk_id == "chunk_1"
    assert sample_chunk.embedding is None


def test_document_chunk_with_embedding(sample_embedding: list[float]) -> None:
    """Spec: DocumentChunk should accept embedding vector."""
    chunk = DocumentChunk(
        content="Test content",
        embedding=sample_embedding,
    )
    assert chunk.embedding == sample_embedding
    assert len(chunk.embedding) == 384


def test_retrieval_result_creation(sample_chunks: list[DocumentChunk]) -> None:
    """Spec: RetrievalResult should contain chunks and scores."""
    result = RetrievalResult(
        chunks=sample_chunks,
        scores=[0.9, 0.8, 0.7],
        query="test query",
        total_results=3,
    )
    assert len(result.chunks) == 3
    assert len(result.scores) == 3
    assert result.query == "test query"
    assert result.total_results == 3


def test_retrieval_result_min_items() -> None:
    """Spec: RetrievalResult should require at least one chunk."""
    with pytest.raises(ValueError):
        RetrievalResult(
            chunks=[],
            scores=[],
            query="test",
            total_results=0,
        )


def test_embedding_request() -> None:
    """Spec: EmbeddingRequest should accept list of texts."""
    request = EmbeddingRequest(
        texts=["text1", "text2", "text3"],
        model="text-embedding-3-small",
    )
    assert len(request.texts) == 3
    assert request.model == "text-embedding-3-small"


def test_embedding_response() -> None:
    """Spec: EmbeddingResponse should contain embeddings and metadata."""
    response = EmbeddingResponse(
        embeddings=[[0.1] * 384, [0.2] * 384],
        model="text-embedding-3-small",
        dimensions=384,
    )
    assert len(response.embeddings) == 2
    assert response.dimensions == 384
    assert response.model == "text-embedding-3-small"
