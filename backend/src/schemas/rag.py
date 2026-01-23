"""Type Specs for RAG (Retrieval-Augmented Generation) system."""

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Spec: Represents a chunk of a document."""

    content: str = Field(..., description="The text content of the chunk")
    metadata: dict = Field(default_factory=dict, description="Metadata associated with the chunk")
    embedding: list[float] | None = Field(None, description="Vector embedding for semantic search")
    chunk_id: str | None = Field(None, description="Unique identifier for the chunk")
    source: str | None = Field(None, description="Source document identifier")
    position: int | None = Field(None, description="Position of chunk in source document")


class RetrievalResult(BaseModel):
    """Spec: Result of a document retrieval operation."""

    chunks: list[DocumentChunk] = Field(
        default_factory=list, description="Retrieved document chunks"
    )
    scores: list[float] = Field(default_factory=list, description="Relevance scores for each chunk")
    query: str = Field(..., description="The query that was used for retrieval")
    total_results: int = Field(default=0, description="Total number of results found")


class EmbeddingRequest(BaseModel):
    """Spec: Request for generating embeddings."""

    texts: list[str] = Field(..., min_items=1, description="Texts to embed")
    model: str | None = Field(None, description="Embedding model to use")


class EmbeddingResponse(BaseModel):
    """Spec: Response with generated embeddings."""

    embeddings: list[list[float]] = Field(..., description="Generated embeddings")
    model: str = Field(..., description="Model used for embeddings")
    dimensions: int = Field(..., description="Dimension of embeddings")
