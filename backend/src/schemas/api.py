"""Type Specs for FastAPI endpoints."""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentUpload(BaseModel):
    """Spec: Request for document upload."""

    filename: str = Field(..., description="Name of the file")
    content: str = Field(..., description="Document content (base64 encoded for binary files)")
    content_type: str = Field(default="text/plain", description="MIME type of the document")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class BatchDocumentUpload(BaseModel):
    """Spec: Request for batch document upload."""

    documents: List[DocumentUpload] = Field(..., description="List of documents to upload")


class DocumentList(BaseModel):
    """Spec: Response with list of documents."""

    documents: List["DocumentInfo"] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")


class BatchDocumentUploadResponse(BaseModel):
    """Spec: Response for batch document upload."""

    documents: List[DocumentInfo] = Field(..., description="Successfully uploaded documents")
    errors: List[dict] = Field(default_factory=list, description="Upload errors")
    total: int = Field(..., description="Total documents processed")
    success_count: int = Field(..., description="Number of successful uploads")
    error_count: int = Field(..., description="Number of failed uploads")


class DocumentInfo(BaseModel):
    """Spec: Information about a document."""

    id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="File name")
    content_type: str = Field(..., description="MIME type")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    chunk_count: int = Field(default=0, description="Number of chunks")
    metadata: dict = Field(default_factory=dict, description="Document metadata")


class QueryRequest(BaseModel):
    """Spec: Request for query processing."""

    query: str = Field(..., min_length=1, description="User query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum score")
    stream: bool = Field(default=False, description="Enable streaming response")


class QueryResponse(BaseModel):
    """Spec: Response from query processing."""

    answer: str = Field(..., description="Generated answer")
    sources: List["SourceInfo"] = Field(default_factory=list, description="Source documents")
    score: float = Field(..., description="Relevance score")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class SourceInfo(BaseModel):
    """Spec: Information about a source document."""

    chunk_id: str = Field(..., description="Chunk identifier")
    content: str = Field(..., description="Chunk content")
    source: str = Field(..., description="Source document")
    score: float = Field(..., description="Relevance score")
    metadata: dict = Field(default_factory=dict, description="Chunk metadata")


class HealthResponse(BaseModel):
    """Spec: Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")


# Update forward references
DocumentList.model_rebuild()
QueryResponse.model_rebuild()
