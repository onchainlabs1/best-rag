"""Agent service for query processing."""

from typing import Iterator
from src.agents.knowledge_agent import KnowledgeAgent
from src.rag.retriever import RAGRetriever
from src.schemas.agents import AgentConfig
from src.schemas.api import QueryRequest, QueryResponse, SourceInfo
import structlog

logger = structlog.get_logger()


class AgentService:
    """Service for processing queries with agents."""

    def __init__(
        self,
        agent: KnowledgeAgent | None = None,
        retriever: RAGRetriever | None = None,
    ) -> None:
        """
        Initialize agent service.

        Args:
            agent: Knowledge agent instance
            retriever: RAG retriever instance
        """
        if retriever is None:
            retriever = RAGRetriever()

        self.retriever = retriever
        self.agent = agent or KnowledgeAgent(retriever=retriever)

    def process_query(
        self,
        request: QueryRequest,
    ) -> QueryResponse:
        """
        Process a query using the agent.

        Args:
            request: Query request

        Returns:
            Query response with answer and sources
        """
        logger.info("processing_query", query=request.query)

        # Update agent config if needed
        config = AgentConfig(
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            stream=request.stream,
        )
        self.agent.config = config

        # Check if there are documents in the collection
        try:
            collection_count = self.retriever.collection.count()
            logger.info("collection_count_before_search", count=collection_count)
            if collection_count == 0:
                error_msg = (
                    "No documents are indexed in the knowledge base.\n\n"
                    "Please upload at least one document before making queries."
                )
                return QueryResponse(
                    answer=error_msg,
                    sources=[],
                    score=0.0,
                    metadata={
                        "error": "no_documents",
                        "message": "No documents indexed",
                        "collection_count": 0,
                    }
                )
        except Exception as e:
            logger.warning("failed_to_count_collection", error=str(e))

        # Process query using agent (agent will handle retrieval internally)
        result = self.agent.query(query=request.query, stream=False)
        
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            logger.error("agent_query_returned_non_dict", result_type=type(result))
            # Se for um generator ou outro tipo, criar um dict vazio
            if hasattr(result, '__dict__'):
                result = result.__dict__
            else:
                result = {
                    "response": "Error processing the query. Please try again.",
                    "citations": [],
                    "validation_score": 0.0,
                    "iteration_count": 0,
                    "metadata": {},
                }

        # Build sources from agent's retrieved documents and citations
        sources: list[SourceInfo] = []
        
        # Get retrieved documents from agent result
        retrieved_docs_list = result.get("retrieved_docs", []) if isinstance(result, dict) else []
        citation_ids = set(result.get("citations", []) if isinstance(result, dict) else [])
        
        # Build sources from retrieved documents
        for doc in retrieved_docs_list:
            if isinstance(doc, dict):
                chunk_id = doc.get("chunk_id", "")
                # Only include documents that were cited
                if chunk_id in citation_ids or len(citation_ids) == 0:
                    source = SourceInfo(
                        chunk_id=chunk_id or "",
                        content=(doc.get("content", "")[:200] + "..." 
                                if len(doc.get("content", "")) > 200 
                                else doc.get("content", "")),
                        source=doc.get("metadata", {}).get("source", "") if isinstance(doc.get("metadata"), dict) else "",
                        score=doc.get("score", 0.0),
                        metadata=doc.get("metadata", {}) if isinstance(doc.get("metadata"), dict) else {},
                    )
                    sources.append(source)
        
        # If no sources but we have citations, try to retrieve them
        if not sources and citation_ids:
            logger.info("retrieving_cited_documents", citation_count=len(citation_ids))
            try:
                # Retrieve specific chunks by ID if possible
                for citation_id in list(citation_ids)[:10]:  # Limit to first 10
                    # Try to get from collection directly
                    try:
                        results = self.retriever.collection.get(ids=[citation_id])
                        if results and results.get("documents"):
                            source = SourceInfo(
                                chunk_id=citation_id,
                                content=results["documents"][0][:200] + "..." if len(results["documents"][0]) > 200 else results["documents"][0],
                                source=results.get("metadatas", [{}])[0].get("source", "") if results.get("metadatas") else "",
                                score=0.0,  # Score not available from direct get
                                metadata=results.get("metadatas", [{}])[0] if results.get("metadatas") else {},
                            )
                            sources.append(source)
                    except Exception:
                        pass
            except Exception as e:
                logger.warning("failed_to_retrieve_cited_documents", error=str(e))

        response = QueryResponse(
            answer=result.get("response", ""),
            sources=sources,
            score=result.get("validation_score", 0.0),
            metadata={
                "iteration_count": result.get("iteration_count", 0),
                "citations_count": len(result.get("citations", [])),
            },
        )

        logger.info("query_processed", score=response.score)

        return response

    def process_query_stream(
        self,
        request: QueryRequest,
    ) -> Iterator[dict]:
        """
        Process a query with streaming response.

        Args:
            request: Query request

        Yields:
            Streaming updates from the agent
        """
        logger.info("processing_query_stream", query=request.query)

        # Update agent config
        config = AgentConfig(
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            stream=True,
        )
        self.agent.config = config

        # Stream query processing
        for state_update in self.agent.query(query=request.query, stream=True):
            yield state_update
