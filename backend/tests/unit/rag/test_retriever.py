"""Test Specs for RAG retriever."""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.rag.retriever import RAGRetriever
from src.rag.embeddings import EmbeddingService
from src.schemas.rag import DocumentChunk, RetrievalResult
from tests.fixtures.rag import sample_chunks, sample_texts


@pytest.fixture
def temp_chroma_path() -> str:
    """Fixture: Temporary directory for ChromaDB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def embedding_service() -> EmbeddingService:
    """Fixture: Embedding service with local model."""
    return EmbeddingService(provider="local", model="all-MiniLM-L6-v2")


@pytest.fixture
def retriever(temp_chroma_path: str, embedding_service: EmbeddingService) -> RAGRetriever:
    """Fixture: RAG retriever with temporary database."""
    import src.config

    original_path = src.config.settings.chroma_path
    src.config.settings.chroma_path = temp_chroma_path

    retriever = RAGRetriever(
        collection_name="test_collection",
        embedding_service=embedding_service,
    )

    yield retriever

    retriever.delete_collection()
    src.config.settings.chroma_path = original_path


def test_retriever_initialization(retriever: RAGRetriever) -> None:
    """Spec: RAGRetriever should initialize with collection."""
    assert retriever.collection_name == "test_collection"
    assert retriever.collection is not None


def test_add_documents(retriever: RAGRetriever, sample_chunks: list[DocumentChunk]) -> None:
    """Spec: add_documents should add chunks to vector database."""
    retriever.add_documents(sample_chunks)
    # Verify by retrieving
    result = retriever.retrieve("first chunk", top_k=1)
    assert len(result.chunks) > 0


def test_retrieve_top_k(retriever: RAGRetriever, sample_chunks: list[DocumentChunk]) -> None:
    """Spec: retrieve should return top-k results."""
    retriever.add_documents(sample_chunks)
    result = retriever.retrieve("chunk", top_k=2)

    assert isinstance(result, RetrievalResult)
    assert len(result.chunks) <= 2
    assert len(result.scores) <= 2


def test_retrieve_score_threshold(
    retriever: RAGRetriever,
    sample_chunks: list[DocumentChunk],
) -> None:
    """Spec: retrieve should filter by score_threshold."""
    retriever.add_documents(sample_chunks)
    result = retriever.retrieve("unrelated query", top_k=10, score_threshold=0.9)

    # With high threshold and unrelated query, might get fewer results
    assert all(score >= 0.9 for score in result.scores)


def test_retrieve_empty_query(retriever: RAGRetriever) -> None:
    """Spec: retrieve should handle empty query."""
    result = retriever.retrieve("")
    assert isinstance(result, RetrievalResult)
    assert result.query == ""
    assert len(result.chunks) == 0
