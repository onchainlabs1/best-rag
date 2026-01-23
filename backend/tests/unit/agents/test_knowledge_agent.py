"""Test Specs for KnowledgeAgent."""


import pytest

from src.agents.knowledge_agent import KnowledgeAgent
from src.rag.embeddings import EmbeddingService
from src.rag.retriever import RAGRetriever
from src.schemas.agents import AgentConfig


@pytest.fixture
def retriever() -> RAGRetriever:
    """Fixture: RAG retriever."""
    embedding_service = EmbeddingService(provider="local", model="all-MiniLM-L6-v2")
    return RAGRetriever(
        collection_name="test_collection",
        embedding_service=embedding_service,
    )


def test_knowledge_agent_initialization(retriever: RAGRetriever) -> None:
    """Spec: KnowledgeAgent should initialize with retriever and config."""
    agent = KnowledgeAgent(retriever=retriever)

    assert agent.retriever is retriever
    assert agent.config is not None
    assert agent.graph is not None


def test_knowledge_agent_custom_config(retriever: RAGRetriever) -> None:
    """Spec: KnowledgeAgent should accept custom config."""
    config = AgentConfig(
        max_iterations=5,
        validation_threshold=0.8,
        top_k=10,
        score_threshold=0.8,
    )

    agent = KnowledgeAgent(retriever=retriever, config=config)

    assert agent.config.max_iterations == 5
    assert agent.config.validation_threshold == 0.8


def test_knowledge_agent_has_graph(retriever: RAGRetriever) -> None:
    """Spec: KnowledgeAgent should have a built graph."""
    agent = KnowledgeAgent(retriever=retriever)

    assert agent.graph is not None
    # Graph should have nodes
    assert hasattr(agent.graph, "nodes") or hasattr(agent.graph, "_nodes")


def test_knowledge_agent_query_method_exists(retriever: RAGRetriever) -> None:
    """Spec: KnowledgeAgent should have query method."""
    agent = KnowledgeAgent(retriever=retriever)

    assert hasattr(agent, "query")
    assert callable(agent.query)
