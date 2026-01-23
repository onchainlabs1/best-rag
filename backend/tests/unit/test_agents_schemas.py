"""Test Specs for agent schemas."""

from src.schemas.agents import AgentConfig, AgentResponse, AgentState


def test_agent_state_initialization() -> None:
    """Spec: AgentState should initialize with query."""
    state = AgentState(query="What is Python?")
    assert state.query == "What is Python?"
    assert state.retrieved_docs == []
    assert state.context == ""
    assert state.response == ""
    assert state.validation_score == 0.0
    assert state.iteration_count == 0
    assert state.citations == []


def test_agent_state_update() -> None:
    """Spec: AgentState should allow updating fields."""
    state = AgentState(query="test query")
    state.context = "Some context"
    state.response = "Some response"
    state.validation_score = 0.85
    state.iteration_count = 1

    assert state.context == "Some context"
    assert state.response == "Some response"
    assert state.validation_score == 0.85
    assert state.iteration_count == 1


def test_agent_response() -> None:
    """Spec: AgentResponse should contain all required fields."""
    response = AgentResponse(
        response="This is the answer.",
        citations=["doc1", "doc2"],
        context_used=["chunk1", "chunk2"],
        validation_score=0.9,
        iteration_count=1,
        metadata={"model": "gpt-4"},
    )
    assert response.response == "This is the answer."
    assert len(response.citations) == 2
    assert len(response.context_used) == 2
    assert response.validation_score == 0.9
    assert response.iteration_count == 1


def test_agent_config_defaults() -> None:
    """Spec: AgentConfig should have sensible defaults."""
    config = AgentConfig()
    assert config.max_iterations == 3
    assert config.validation_threshold == 0.7
    assert config.top_k == 5
    assert config.score_threshold == 0.7
    assert config.stream is False


def test_agent_config_custom() -> None:
    """Spec: AgentConfig should accept custom values."""
    config = AgentConfig(
        max_iterations=5,
        validation_threshold=0.8,
        top_k=10,
        score_threshold=0.85,
        stream=True,
    )
    assert config.max_iterations == 5
    assert config.validation_threshold == 0.8
    assert config.top_k == 10
    assert config.score_threshold == 0.85
    assert config.stream is True
