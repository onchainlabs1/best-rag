"""Knowledge agent using LangGraph."""


import structlog
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from src.agents.nodes import (
    finalize_node,
    generate_node,
    refine_node,
    retrieve_node,
    validate_node,
)
from src.agents.state import AgentState
from src.config import settings
from src.observability.tracing import get_tracer
from src.rag.retriever import RAGRetriever
from src.schemas.agents import AgentConfig

# Import trace for status codes
try:
    from opentelemetry import trace
except ImportError:
    trace = None

logger = structlog.get_logger()


class KnowledgeAgent:
    """LangGraph-based agent for knowledge base queries."""

    def __init__(
        self,
        retriever: RAGRetriever,
        config: AgentConfig | None = None,
    ) -> None:
        """
        Initialize knowledge agent.

        Args:
            retriever: RAG retriever instance
            config: Agent configuration
        """
        self.retriever = retriever
        self.config = config or AgentConfig()

        # Initialize LLM (suporta modo local ou OpenAI)
        self.llm = self._init_llm()

        # Build graph
        self.graph = self._build_graph()

    def _init_llm(self):
        """Initialize LLM based on provider setting."""
        provider = settings.llm_provider

        if provider == "local":
            # Para modo local, usar um LLM mock ou deixar opcional
            # Por enquanto, usar OpenAI mesmo (pode ser configurado depois)
            logger.warning("LLM_PROVIDER=local not fully supported yet. Using OpenAI.")
            provider = "openai"

        if provider == "groq":
            try:
                from langchain_groq import ChatGroq
            except ImportError as err:
                raise ImportError(
                    "langchain-groq is not installed. Install with: pip install langchain-groq"
                ) from err

            api_key = settings.groq_api_key or ""
            if not api_key:
                raise ValueError("Groq API key not configured. Set GROQ_API_KEY in the .env file")

            logger.info("using_groq_llm", model=settings.llm_model)
            return ChatGroq(
                groq_api_key=api_key,
                model_name=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        elif provider == "openai":
            api_key = settings.openai_api_key or ""
            if not api_key:
                logger.warning("OpenAI API key not configured. Some features may not work.")
            return ChatOpenAI(
                api_key=api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError as err:
                raise ImportError(
                    "langchain-anthropic is not installed. Install with: pip install langchain-anthropic"
                ) from err

            api_key = settings.anthropic_api_key or ""
            if not api_key:
                raise ValueError(
                    "Anthropic API key not configured. Set ANTHROPIC_API_KEY in the .env file"
                )

            logger.info("using_anthropic_llm", model=settings.llm_model)
            return ChatAnthropic(
                anthropic_api_key=api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _build_graph(self) -> StateGraph:
        """Build LangGraph state graph."""
        # Create graph
        workflow = StateGraph(AgentState)

        # Add nodes
        # Use closure to capture config values
        def retrieve_wrapper(state: AgentState) -> AgentState:
            return retrieve_node(
                state,
                self.retriever,
                self.config.top_k,
                self.config.score_threshold,
                self.config.search_type,
                self.config.alpha,
            )

        workflow.add_node("retrieve", retrieve_wrapper)
        workflow.add_node(
            "generate",
            lambda state: generate_node(state, self.llm, self.config.validation_threshold),
        )
        workflow.add_node(
            "validate",
            lambda state: validate_node(state, self.llm, self.config.validation_threshold),
        )
        def refine_wrapper(state: AgentState) -> AgentState:
            return refine_node(
                state,
                self.retriever,
                self.llm,
                self.config.top_k,
                self.config.score_threshold,
                self.config.search_type,
                self.config.alpha,
            )

        workflow.add_node("refine", refine_wrapper)
        workflow.add_node("finalize", finalize_node)

        # Add edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "validate")

        # Conditional edge: refine or finalize
        def should_refine(state: AgentState) -> str:
            score = state.get("validation_score", 0.0)
            iteration = state.get("iteration_count", 0)
            threshold = self.config.validation_threshold
            max_iter = self.config.max_iterations

            if score < threshold and iteration < max_iter:
                return "refine"
            return "finalize"

        workflow.add_conditional_edges(
            "validate",
            should_refine,
            {
                "refine": "refine",
                "finalize": "finalize",
            },
        )

        workflow.add_edge("refine", "validate")  # Loop back to validate
        workflow.add_edge("finalize", END)

        # Compile graph with optional checkpointing
        if settings.checkpointing_enabled:
            try:
                from langgraph.checkpoint.sqlite import SqliteSaver

                checkpointer = SqliteSaver.from_conn_string(settings.checkpoint_path)
                return workflow.compile(checkpointer=checkpointer)
            except ImportError:
                logger.warning(
                    "checkpointing_not_available",
                    message="LangGraph checkpointing not available. Install langgraph with checkpointing support.",
                )
                return workflow.compile()
        else:
            return workflow.compile()

    def query(
        self,
        query: str,
        stream: bool = False,
    ):
        """
        Process a query using the agent.

        Args:
            query: User query
            stream: Whether to stream responses

        Returns:
            Agent response with answer and metadata (dict) or generator if stream=True
        """
        logger.info("agent_query", query=query)

        # Start tracing span if available
        tracer = get_tracer(__name__)
        span = None
        if tracer:
            span = tracer.start_as_current_span("agent.query")
            span.set_attribute("query", query)
            span.set_attribute("stream", stream)

        try:
            # Initial state
            initial_state: AgentState = {
                "query": query,
                "retrieved_docs": [],
                "context": "",
                "response": "",
                "validation_score": 0.0,
                "iteration_count": 0,
                "citations": [],
                "metadata": {},
            }

            # Run graph - separar streaming de non-streaming para evitar generator
            if stream:
                result = self._query_stream(initial_state)
            else:
                result = self._query_invoke(initial_state)

            # End tracing span
            if span:
                span.set_attribute("stream", stream)
                span.end()

            return result
        except Exception as e:
            # End tracing span with error
            if span:
                if trace:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.end()
            raise

    def _query_stream(self, initial_state: AgentState):
        """Stream query processing."""
        final_state = None
        for state in self.graph.stream(initial_state):
            final_state = state
            yield state
        if final_state:
            yield final_state

    def _query_invoke(self, initial_state: AgentState) -> dict:
        """Invoke query processing (non-streaming)."""
        try:
            final_state = self.graph.invoke(initial_state)

            # LangGraph may return a dictionary or an object
            # Ensure we always work with a dictionary
            if not isinstance(final_state, dict):
                # If it's an object, try to convert
                if hasattr(final_state, "__dict__"):
                    final_state = final_state.__dict__
                elif hasattr(final_state, "keys"):
                    # It's a dict-like object
                    final_state = dict(final_state)
                else:
                    logger.error("unexpected_final_state_type", state_type=type(final_state))
                    # Return initial state if we can't convert
                    final_state = initial_state

            # Ensure we have a valid dictionary
            if not isinstance(final_state, dict):
                logger.error("final_state_not_dict_after_conversion", state_type=type(final_state))
                final_state = initial_state

            return {
                "response": final_state.get("response", ""),
                "citations": final_state.get("citations", []),
                "retrieved_docs": final_state.get(
                    "retrieved_docs", []
                ),  # Include retrieved docs for source building
                "context_used": [
                    doc.get("chunk_id", "") if isinstance(doc, dict) else ""
                    for doc in final_state.get("retrieved_docs", [])
                ],
                "validation_score": final_state.get("validation_score", 0.0),
                "iteration_count": final_state.get("iteration_count", 0),
                "metadata": final_state.get("metadata", {}),
            }
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            logger.error(
                "agent_query_failed",
                error=str(e),
                error_type=type(e).__name__,
                traceback=error_trace,
            )

            # More specific error message
            error_msg = str(e)
            if "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                error_msg = (
                    "Authentication error: API key is not configured or is invalid. "
                    "Set GROQ_API_KEY or OPENAI_API_KEY in the .env file"
                )
            elif "rate limit" in error_msg.lower():
                error_msg = "Rate limit exceeded. Please try again in a few moments."
            elif "model" in error_msg.lower() and (
                "not found" in error_msg.lower() or "decommissioned" in error_msg.lower()
            ):
                error_msg = "Model not found or decommissioned. Check the model configuration in the .env file"
            else:
                error_msg = f"Error processing query: {error_msg}"

            # Return error response in valid format
            return {
                "response": error_msg,
                "citations": [],
                "context_used": [],
                "validation_score": 0.0,
                "iteration_count": 0,
                "metadata": {"error": str(e), "error_type": type(e).__name__},
            }
