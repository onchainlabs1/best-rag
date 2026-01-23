"""Fixtures for RAG system tests."""

import pytest

from src.schemas.rag import DocumentChunk, RetrievalResult


@pytest.fixture
def sample_chunk() -> DocumentChunk:
    """Fixture: Sample document chunk."""
    return DocumentChunk(
        content="This is a sample document chunk for testing.",
        metadata={"source": "test_doc.txt", "position": 0},
        chunk_id="chunk_1",
        source="test_doc",
        position=0,
    )


@pytest.fixture
def sample_chunks() -> list[DocumentChunk]:
    """Fixture: List of sample document chunks."""
    return [
        DocumentChunk(
            content="First chunk of document.",
            metadata={"source": "test.txt", "position": 0},
            chunk_id="chunk_1",
            source="test",
            position=0,
        ),
        DocumentChunk(
            content="Second chunk of document.",
            metadata={"source": "test.txt", "position": 1},
            chunk_id="chunk_2",
            source="test",
            position=1,
        ),
        DocumentChunk(
            content="Third chunk of document.",
            metadata={"source": "test.txt", "position": 2},
            chunk_id="chunk_3",
            source="test",
            position=2,
        ),
    ]


@pytest.fixture
def sample_retrieval_result(sample_chunks: list[DocumentChunk]) -> RetrievalResult:
    """Fixture: Sample retrieval result."""
    return RetrievalResult(
        chunks=sample_chunks,
        scores=[0.95, 0.88, 0.75],
        query="test query",
        total_results=3,
    )


@pytest.fixture
def sample_embedding() -> list[float]:
    """Fixture: Sample embedding vector."""
    return [0.1] * 384  # 384-dimensional embedding (common for sentence transformers)


@pytest.fixture
def sample_texts() -> list[str]:
    """Fixture: Sample texts for embedding."""
    return [
        "This is the first text to embed.",
        "This is the second text to embed.",
        "This is the third text to embed.",
    ]
