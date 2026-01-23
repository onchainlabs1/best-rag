"""Query expansion service for improving retrieval recall."""

import structlog

from src.config import settings

logger = structlog.get_logger()


class QueryExpander:
    """Service for expanding queries to improve retrieval recall."""

    def __init__(self, use_llm: bool = True) -> None:
        """
        Initialize query expander.

        Args:
            use_llm: Whether to use LLM for expansion (default: True)
        """
        self.use_llm = use_llm
        self._llm = None

    def _init_llm(self) -> None:
        """Initialize LLM for query expansion."""
        if self._llm is not None:
            return

        try:
            provider = settings.llm_provider

            if provider == "groq":
                from langchain_groq import ChatGroq

                api_key = settings.groq_api_key or ""
                if not api_key:
                    logger.warning("groq_api_key_not_set", message="LLM expansion disabled")
                    return

                self._llm = ChatGroq(
                    groq_api_key=api_key,
                    model_name=settings.llm_model,
                    temperature=0.3,
                    max_tokens=100,
                )
            elif provider == "openai":
                from langchain_openai import ChatOpenAI

                api_key = settings.openai_api_key or ""
                if not api_key:
                    logger.warning("openai_api_key_not_set", message="LLM expansion disabled")
                    return

                self._llm = ChatOpenAI(
                    api_key=api_key,
                    model=settings.llm_model,
                    temperature=0.3,
                    max_tokens=100,
                )
            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic

                api_key = settings.anthropic_api_key or ""
                if not api_key:
                    logger.warning("anthropic_api_key_not_set", message="LLM expansion disabled")
                    return

                self._llm = ChatAnthropic(
                    anthropic_api_key=api_key,
                    model=settings.llm_model,
                    temperature=0.3,
                    max_tokens=100,
                )

            logger.info("query_expander_llm_initialized", provider=provider)
        except ImportError as err:
            logger.warning("llm_import_failed", error=str(err), message="LLM expansion disabled")
        except Exception as e:
            logger.error("llm_init_failed", error=str(e))

    def expand(self, query: str) -> str:
        """
        Expand query with synonyms and variations.

        Args:
            query: Original query

        Returns:
            Expanded query (original + expansions)
        """
        if not self.use_llm:
            return query

        self._init_llm()

        if self._llm is None:
            # Fallback: return original query
            return query

        try:
            from langchain_core.prompts import ChatPromptTemplate

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a query expansion assistant. Given a search query, generate 2-3 synonyms or related terms that would help find relevant documents. Return only the expanded terms, separated by spaces.",
                    ),
                    ("human", "Query: {query}\n\nExpanded terms:"),
                ]
            )

            chain = prompt | self._llm
            response = chain.invoke({"query": query})

            expanded_terms = response.content.strip() if hasattr(response, "content") else str(response).strip()

            # Combine original query with expanded terms
            expanded_query = f"{query} {expanded_terms}"

            logger.info("query_expanded", original=query, expanded=expanded_query)
            return expanded_query
        except Exception as e:
            logger.error("query_expansion_failed", error=str(e))
            # Fallback: return original query
            return query
