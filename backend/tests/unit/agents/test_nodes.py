"""Test Specs for agent nodes."""

from unittest.mock import Mock

import pytest

from src.agents.nodes import (
    finalize_node,
    generate_node,
    retrieve_node,
    validate_node,
)
from src.agents.state import AgentState
from src.rag.retriever import RAGRetriever
from src.schemas.rag import DocumentChunk


@pytest.fixture
def retriever() -> RAGRetriever:
    """Fixture: Mock retriever."""
    from src.rag.embeddings import EmbeddingService
    embedding_service = EmbeddingService(provider="local", model="all-MiniLM-L6-v2")
    return RAGRetriever(
        collection_name="test_collection",
        embedding_service=embedding_service,
    )


@pytest.fixture
def sample_state() -> AgentState:
    """Fixture: Sample agent state."""
    return {
        "query": "What is Python?",
        "retrieved_docs": [],
        "context": "",
        "response": "",
        "validation_score": 0.0,
        "iteration_count": 0,
        "citations": [],
        "metadata": {},
    }


def test_retrieve_node(retriever: RAGRetriever, sample_state: AgentState) -> None:
    """Spec: retrieve_node should retrieve documents and update state."""
    # Add some documents first
    chunks = [
        DocumentChunk(
            content="Python is a programming language.",
            metadata={"source": "doc1"},
            chunk_id="chunk_1",
            source="doc1",
            position=0,
        ),
    ]
    retriever.add_documents(chunks)

    updated_state = retrieve_node(sample_state, retriever, top_k=5, score_threshold=0.0)

    assert len(updated_state["retrieved_docs"]) > 0
    assert updated_state["context"] != ""


def test_retrieve_node_empty_query(retriever: RAGRetriever) -> None:
    """Spec: retrieve_node should handle empty query."""
    state: AgentState = {
        "query": "",
        "retrieved_docs": [],
        "context": "",
        "response": "",
        "validation_score": 0.0,
        "iteration_count": 0,
        "citations": [],
        "metadata": {},
    }

    updated_state = retrieve_node(state, retriever, top_k=5, score_threshold=0.7)

    # Should not crash, may have empty results
    assert isinstance(updated_state["retrieved_docs"], list)


def test_generate_node(sample_state: AgentState) -> None:
    """Spec: generate_node should generate response from context."""
    sample_state["context"] = "Python is a programming language."
    sample_state["retrieved_docs"] = [
        {
            "content": "Python is a programming language.",
            "metadata": {"source": "doc1"},
            "score": 0.9,
        },
    ]

    # Mock LLM
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Python is a high-level programming language.")

    updated_state = generate_node(sample_state, mock_llm)

    # Should have response
    assert updated_state["response"] != ""
    assert len(updated_state["citations"]) > 0


def test_validate_node(sample_state: AgentState) -> None:
    """Spec: validate_node should calculate validation score."""
    sample_state["response"] = "Python is a programming language."
    sample_state["context"] = "Python is a programming language."

    updated_state = validate_node(sample_state)

    # Should have validation score
    assert "validation_score" in updated_state
    assert isinstance(updated_state["validation_score"], float)
    assert 0.0 <= updated_state["validation_score"] <= 1.0


def test_finalize_node(sample_state: AgentState) -> None:
    """Spec: finalize_node should prepare final response."""
    sample_state["response"] = "Python is a programming language."
    sample_state["citations"] = ["doc1", "doc2"]
    sample_state["validation_score"] = 0.9

    updated_state = finalize_node(sample_state)

    # Should have final response
    assert updated_state["response"] != ""
    assert len(updated_state["citations"]) > 0
