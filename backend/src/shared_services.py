"""Shared service instances to ensure data consistency."""

from src.services.document_service import DocumentService
from src.services.agent_service import AgentService
from src.rag.retriever import RAGRetriever

# Create a single shared instance of the retriever
# This ensures that DocumentService and AgentService access the same data
shared_retriever = RAGRetriever()

# Create services using the same retriever
document_service = DocumentService(retriever=shared_retriever)
agent_service = AgentService(retriever=shared_retriever)
