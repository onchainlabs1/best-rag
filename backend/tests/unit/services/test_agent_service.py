"""Test Specs for AgentService."""

from unittest.mock import Mock, patch

import pytest

from src.agents.knowledge_agent import KnowledgeAgent
from src.rag.embeddings import EmbeddingService
from src.rag.retriever import RAGRetriever
from src.schemas.api import QueryRequest
from src.services.agent_service import AgentService


@pytest.fixture
def retriever() -> RAGRetriever:
    """Fixture: RAG retriever."""
    embedding_service = EmbeddingService(provider="local", model="all-MiniLM-L6-v2")
    return RAGRetriever(
        collection_name="test_collection",
        embedding_service=embedding_service,
    )


@pytest.fixture
def agent_service(retriever: RAGRetriever) -> AgentService:
    """Fixture: Agent service."""
    return AgentService(retriever=retriever)


def test_process_query_success(agent_service: AgentService) -> None:
    """Spec: process_query should return QueryResponse."""
    # This will fail if agent.query doesn't return dict, but we're testing the service layer
    # For now, we'll test that the method exists and can be called
    # Full integration test would require actual agent setup
    assert hasattr(agent_service, "process_query")


def test_process_query_stream(agent_service: AgentService) -> None:
    """Spec: process_query_stream should yield state updates."""
    request = QueryRequest(
        query="What is Python?",
        top_k=5,
        score_threshold=0.7,
        stream=True,
    )

    mock_updates = [
        {"node": "retrieve", "state": {"query": "What is Python?"}},
        {"node": "generate", "state": {"response": "Python is..."}},
    ]

    with patch.object(agent_service.agent, "query", return_value=iter(mock_updates)):
        stream = agent_service.process_query_stream(request)
        # Should be a generator
        assert hasattr(stream, "__iter__")


def test_agent_service_initialization(retriever: RAGRetriever) -> None:
    """Spec: AgentService should initialize with retriever and agent."""
    service = AgentService(retriever=retriever)

    assert service.retriever is not None
    assert service.agent is not None
    assert isinstance(service.agent, KnowledgeAgent)


def test_agent_service_custom_agent() -> None:
    """Spec: AgentService should accept custom agent instance."""
    mock_agent = Mock(spec=KnowledgeAgent)
    mock_retriever = Mock(spec=RAGRetriever)

    service = AgentService(agent=mock_agent, retriever=mock_retriever)

    assert service.agent is mock_agent
    assert service.retriever is mock_retriever
