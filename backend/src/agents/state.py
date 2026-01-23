"""Typed state for LangGraph agent."""

from typing import TypedDict


class AgentState(TypedDict):
    """Typed state managed by LangGraph agent."""

    query: str
    retrieved_docs: list[dict]
    context: str
    response: str
    validation_score: float
    iteration_count: int
    citations: list[str]
    metadata: dict
