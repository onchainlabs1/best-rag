"""Re-ranking service using Cross-Encoder models."""

import structlog

logger = structlog.get_logger()


class Reranker:
    """Re-ranker for improving retrieval results using Cross-Encoder models."""

    def __init__(self, model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        """
        Initialize re-ranker.

        Args:
            model: Cross-Encoder model name
        """
        self.model_name = model
        self.model = None
        self._init_model()

    def _init_model(self) -> None:
        """Initialize Cross-Encoder model."""
        try:
            from sentence_transformers import CrossEncoder

            logger.info("loading_reranker_model", model=self.model_name)
            self.model = CrossEncoder(self.model_name)
            logger.info("reranker_model_loaded", model=self.model_name)
        except ImportError:
            logger.warning(
                "sentence_transformers_not_available",
                message="sentence-transformers required for re-ranking. Install with: pip install sentence-transformers",
            )
            self.model = None
        except Exception as e:
            logger.error("reranker_init_failed", error=str(e), model=self.model_name)
            self.model = None

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[tuple[str, float]]:
        """
        Re-rank documents based on query relevance.

        Args:
            query: Search query
            documents: List of document texts to re-rank
            top_k: Number of top results to return (None = return all)

        Returns:
            List of (document, score) tuples sorted by relevance (highest first)
        """
        if self.model is None:
            logger.warning("reranker_not_available", message="Returning documents without re-ranking")
            # Return documents with default scores
            return [(doc, 0.5) for doc in documents]

        if not documents:
            return []

        try:
            # Create query-document pairs
            pairs = [[query, doc] for doc in documents]

            # Get scores from Cross-Encoder
            scores = self.model.predict(pairs)

            # Combine documents with scores and sort by score (descending)
            scored_docs = list(zip(documents, scores, strict=False))
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            # Return top-k if specified
            if top_k is not None:
                return scored_docs[:top_k]

            return scored_docs
        except Exception as e:
            logger.error("rerank_error", error=str(e))
            # Fallback: return documents with default scores
            return [(doc, 0.5) for doc in documents]

    def is_available(self) -> bool:
        """Check if re-ranker is available."""
        return self.model is not None
