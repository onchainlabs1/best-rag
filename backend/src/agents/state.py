"""Typed state for LangGraph agent."""

from typing import List, TypedDict


class AgentState(TypedDict):
    """Typed state managed by LangGraph agent."""

    query: str
    retrieved_docs: List[dict]
    context: str
    response: str
    validation_score: float
    iteration_count: int
    citations: List[str]
    metadata: dict
