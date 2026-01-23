"""Nodes for LangGraph agent."""

from typing import Literal

import structlog
from langchain_openai import ChatOpenAI

try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    # Fallback for older LangChain versions
    from langchain.prompts import ChatPromptTemplate

from src.agents.state import AgentState
from src.rag.retriever import RAGRetriever

logger = structlog.get_logger()

# Constants
REFINE_THRESHOLD_MULTIPLIER = 0.7  # Use 70% of original threshold for refinement


def retrieve_node(
    state: AgentState,
    retriever: RAGRetriever,
    top_k: int = 5,
    score_threshold: float = 0.7,  # Default from AgentConfig, will be overridden by config
    search_type: Literal["vector", "bm25", "hybrid"] | None = None,
    alpha: float | None = None,
) -> AgentState:
    """
    Retrieve relevant documents using RAG.

    Args:
        state: Current agent state
        retriever: RAG retriever instance
        top_k: Number of documents to retrieve
        score_threshold: Minimum similarity score threshold
        search_type: Type of search ("vector", "bm25", "hybrid")
        alpha: Weight for hybrid search

    Returns:
        Updated state with retrieved documents
    """
    query = state.get("query", "")
    logger.info(
        "retrieving_documents",
        query=query,
        top_k=top_k,
        score_threshold=score_threshold,
        search_type=search_type,
    )

    # Use provided score_threshold (from config or request)
    result = retriever.retrieve(
        query,
        top_k=top_k,
        score_threshold=score_threshold,
        search_type=search_type,
        alpha=alpha,
    )

    # Update state
    retrieved_docs = [
        {
            "content": chunk.content,
            "metadata": chunk.metadata,
            "score": score,
            "chunk_id": chunk.chunk_id,
        }
        for chunk, score in zip(result.chunks, result.scores, strict=False)
    ]

    state["retrieved_docs"] = retrieved_docs
    logger.info("documents_retrieved", count=len(retrieved_docs))

    return state


def generate_node(
    state: AgentState,
    llm: ChatOpenAI,
    validation_threshold: float = 0.7,
) -> AgentState:
    """
    Generate response using LLM with retrieved context.

    Args:
        state: Current agent state
        llm: LLM instance
        validation_threshold: Minimum validation score

    Returns:
        Updated state with generated response
    """
    query = state.get("query", "")
    retrieved_docs = state.get("retrieved_docs", [])
    iteration = state.get("iteration_count", 0)

    logger.info("generating_response", query=query, iteration=iteration)

    # Build context from retrieved documents
    # Improved context formatting for better LLM understanding
    context_parts: list[str] = []
    citations: list[str] = []

    if not retrieved_docs:
        logger.warning("no_documents_retrieved", query=query)
        state["context"] = "No relevant documents were found in the knowledge base."
        state["response"] = (
            "I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing your question or upload more documents."
        )
        state["citations"] = []
        return state

    for idx, doc in enumerate(retrieved_docs):
        content = doc.get("content", "").strip()
        chunk_id = doc.get("chunk_id", f"doc_{idx}")
        score = doc.get("score", 0.0)

        # Format: Clear source identification with content
        # Put chunk_id at the end for easier citation
        context_parts.append(f"DOCUMENT EXCERPT [{chunk_id}] (Relevance: {score:.1%}):\n{content}")
        citations.append(chunk_id)

    # Join with clear separators
    context = "\n\n" + "=" * 80 + "\n\n".join(context_parts) + "\n\n" + "=" * 80
    state["context"] = context
    state["citations"] = citations

    # Create prompt with context
    # Improved prompt for more specific and direct responses
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert assistant that answers questions based EXCLUSIVELY on the provided document context. "
                "Your answers must be SPECIFIC, DETAILED, and DIRECTLY based on the content provided.\n\n"
                "CRITICAL RULES:\n"
                "- Answer ONLY using information from the context below\n"
                "- NEVER invent, generalize, or create categories that are not explicitly in the context\n"
                "- If asked about multiple documents, list each document separately with its specific content\n"
                "- Each different piece of information MUST use a DIFFERENT chunk_id citation\n"
                "- Do NOT reuse the same chunk_id for different information\n"
                "- Quote EXACT text from the context when possible - do not paraphrase into generic categories\n"
                "- If the context mentions specific document types or names, use those EXACTLY\n"
                "- If information is missing, say exactly what is missing, don't generalize\n"
                "- Do NOT create lists of document types unless they are explicitly listed in the context\n\n"
                "Citation rules:\n"
                "- Use [chunk_id: {chunk_id}] format for citations\n"
                "- Each unique fact or piece of information must have its own citation\n"
                "- If multiple chunks contain similar information, cite each one separately\n"
                "- Never use the same chunk_id citation multiple times unless referring to the exact same information\n\n"
                "Answer format:\n"
                "- Start with a direct answer to the question\n"
                "- Quote or summarize the ACTUAL content from the context\n"
                "- If listing documents, describe what each document ACTUALLY contains based on the context\n"
                "- Use specific citations [chunk_id: ...] for each piece of information\n"
                "- Be concrete and factual, not abstract or generic",
            ),
            (
                "human",
                "DOCUMENT CONTENT:\n{context}\n\nUSER QUESTION: {query}\n\nProvide a SPECIFIC and DETAILED answer using ONLY the information from the document content above. Quote actual content and cite each piece of information with its specific chunk_id:",
            ),
        ]
    )

    response_text = ""
    try:
        chain = prompt | llm
        response = chain.invoke({"context": context, "query": query})

        response_text = response.content if hasattr(response, "content") else str(response)
        state["response"] = response_text
    except Exception as e:
        logger.error("llm_generation_failed", error=str(e), error_type=type(e).__name__)
        # If it fails, return a helpful error message
        error_msg = str(e)
        if "api key" in error_msg.lower() or "authentication" in error_msg.lower():
            response_text = (
                "Error: API key is not configured correctly. "
                "Check the settings in the backend .env file."
            )
        elif "model" in error_msg.lower() and (
            "decommissioned" in error_msg.lower() or "not found" in error_msg.lower()
        ):
            response_text = (
                "Error: The configured model is not available. "
                "Check LLM_MODEL in the .env file. Available Groq models: llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768"
            )
        else:
            response_text = f"Error generating response: {error_msg}"

        state["response"] = response_text
        state["validation_score"] = 0.0

    logger.info("response_generated", length=len(response_text), iteration=iteration)

    return state


def validate_node(
    state: AgentState,
    llm: ChatOpenAI,
    validation_threshold: float = 0.7,
) -> AgentState:
    """
    Validate response quality using LLM judge.

    Args:
        state: Current agent state
        llm: LLM instance for validation
        validation_threshold: Minimum acceptable score

    Returns:
        Updated state with validation score
    """
    query = state.get("query", "")
    response = state.get("response", "")
    context = state.get("context", "")

    logger.info("validating_response", query=query)

    # Create validation prompt - improved for better evaluation
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a quality assessment expert. Evaluate the answer quality on a scale from 0.0 to 1.0.\n\n"
                "Evaluation criteria (weighted):\n"
                "1. Relevance (30%): Does the answer directly address the question?\n"
                "2. Completeness (30%): Does the answer provide sufficient information?\n"
                "3. Accuracy (40%): Is the answer factually correct based on the provided context?\n\n"
                "Respond with ONLY a single float number between 0.0 and 1.0 (e.g., 0.85).",
            ),
            (
                "human",
                "Question: {query}\n\n"
                "Context provided:\n{context}\n\n"
                "Answer to evaluate:\n{response}\n\n"
                "Quality score (0.0-1.0):",
            ),
        ]
    )

    try:
        chain = prompt | llm
        validation_response = chain.invoke(
            {"query": query, "context": context, "response": response}
        )

        validation_text = (
            validation_response.content
            if hasattr(validation_response, "content")
            else str(validation_response)
        )
    except Exception as e:
        logger.error("llm_validation_failed", error=str(e))
        # If validation fails, use default score
        validation_text = "0.5"

    # Parse score
    try:
        score = float(validation_text.strip())
        score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
    except ValueError:
        # If parsing fails, use a default score
        score = 0.5
        logger.warning("validation_score_parse_failed", response=validation_text)

    state["validation_score"] = score

    logger.info("response_validated", score=score, threshold=validation_threshold)

    return state


def refine_node(
    state: AgentState,
    retriever: RAGRetriever,
    llm: ChatOpenAI,
    top_k: int = 5,
    score_threshold: float = 0.7,  # Default from AgentConfig, will be overridden by config
    search_type: Literal["vector", "bm25", "hybrid"] | None = None,
    alpha: float | None = None,
) -> AgentState:
    """
    Refine response by retrieving additional documents.

    Args:
        state: Current agent state
        retriever: RAG retriever instance
        llm: LLM instance
        top_k: Number of additional documents to retrieve
        score_threshold: Minimum similarity score threshold
        search_type: Type of search ("vector", "bm25", "hybrid")
        alpha: Weight for hybrid search

    Returns:
        Updated state with refined response
    """
    query = state.get("query", "")
    iteration = state.get("iteration_count", 0) + 1

    logger.info(
        "refining_response", query=query, iteration=iteration, score_threshold=score_threshold
    )

    # Retrieve more documents (expand search) with lower threshold for refinement
    # Use 70% of original threshold to expand search, but respect user's minimum
    refined_threshold = score_threshold * REFINE_THRESHOLD_MULTIPLIER
    result = retriever.retrieve(
        query,
        top_k=top_k * 2,
        score_threshold=refined_threshold,
        search_type=search_type,
        alpha=alpha,
    )

    # Merge with existing retrieved docs
    existing_ids = {doc.get("chunk_id") for doc in state.get("retrieved_docs", [])}
    new_docs = [
        {
            "content": chunk.content,
            "metadata": chunk.metadata,
            "score": score,
            "chunk_id": chunk.chunk_id,
        }
        for chunk, score in zip(result.chunks, result.scores, strict=False)
        if chunk.chunk_id not in existing_ids
    ]

    state["retrieved_docs"].extend(new_docs)
    state["iteration_count"] = iteration

    # Regenerate with expanded context
    state = generate_node(state, llm)

    return state


def finalize_node(state: AgentState) -> AgentState:
    """
    Finalize response with formatting and metadata.

    Args:
        state: Current agent state

    Returns:
        Finalized state
    """
    logger.info("finalizing_response", score=state.get("validation_score"))

    # Add any final metadata
    state["metadata"] = {
        "finalized": True,
        "validation_score": state.get("validation_score", 0.0),
        "iteration_count": state.get("iteration_count", 0),
        "citations_count": len(state.get("citations", [])),
    }

    return state
