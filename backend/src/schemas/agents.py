"""Type Specs for LangGraph agents."""

from typing import List, Literal
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Spec: State managed by LangGraph agent."""

    query: str = Field(..., description="User query")
    retrieved_docs: List[dict] = Field(default_factory=list, description="Retrieved documents")
    context: str = Field(default="", description="Context assembled from retrieved docs")
    response: str = Field(default="", description="Generated response")
    validation_score: float = Field(default=0.0, description="Quality score of response")
    iteration_count: int = Field(default=0, description="Number of refinement iterations")
    citations: List[str] = Field(default_factory=list, description="Citations for sources")


class AgentResponse(BaseModel):
    """Spec: Final response from agent."""

    response: str = Field(..., description="Generated response text")
    citations: List[str] = Field(default_factory=list, description="Source citations")
    context_used: List[str] = Field(default_factory=list, description="Context chunks used")
    validation_score: float = Field(..., description="Quality score")
    iteration_count: int = Field(..., description="Number of iterations")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class AgentConfig(BaseModel):
    """Spec: Configuration for agent execution."""

    max_iterations: int = Field(default=3, description="Maximum refinement iterations")
    validation_threshold: float = Field(default=0.7, description="Minimum validation score")
    top_k: int = Field(default=5, description="Number of documents to retrieve")
    score_threshold: float = Field(default=0.7, description="Minimum retrieval score")
    stream: bool = Field(default=False, description="Enable streaming responses")


class NodeOutput(BaseModel):
    """Spec: Output from a LangGraph node."""

    node_name: str = Field(..., description="Name of the node")
    output: dict = Field(..., description="Node output data")
    state: dict = Field(..., description="Updated state")
