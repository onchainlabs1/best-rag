"""Caching service for embeddings and queries."""

import hashlib
import time
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class TTLCache:
    """Time-based cache with TTL (Time To Live)."""

    def __init__(self, ttl: int = 3600) -> None:
        """
        Initialize TTL cache.

        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.ttl = ttl
        self._cache: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl:
            # Expired, remove from cache
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def size(self) -> int:
        """Get number of cached items."""
        # Clean expired entries first
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items() if current_time - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self._cache[key]

        return len(self._cache)


class EmbeddingCache:
    """Cache for embeddings."""

    def __init__(self, ttl: int = 3600) -> None:
        """
        Initialize embedding cache.

        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.cache = TTLCache(ttl=ttl)
        logger.info("embedding_cache_initialized", ttl=ttl)

    def _make_key(self, text: str, model: str) -> str:
        """Generate cache key from text and model."""
        key_string = f"{text}:{model}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, text: str, model: str) -> list[float] | None:
        """
        Get cached embedding.

        Args:
            text: Text that was embedded
            model: Model used for embedding

        Returns:
            Cached embedding or None
        """
        key = self._make_key(text, model)
        return self.cache.get(key)

    def set(self, text: str, model: str, embedding: list[float]) -> None:
        """
        Cache embedding.

        Args:
            text: Text that was embedded
            model: Model used for embedding
            embedding: Embedding vector
        """
        key = self._make_key(text, model)
        self.cache.set(key, embedding)

    def clear(self) -> None:
        """Clear all cached embeddings."""
        self.cache.clear()


class QueryCache:
    """Cache for query results."""

    def __init__(self, ttl: int = 300) -> None:
        """
        Initialize query cache.

        Args:
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.cache = TTLCache(ttl=ttl)
        logger.info("query_cache_initialized", ttl=ttl)

    def _make_key(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        search_type: str | None = None,
        alpha: float | None = None,
    ) -> str:
        """Generate cache key from query parameters."""
        key_string = f"{query}:{top_k}:{score_threshold}:{search_type}:{alpha}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        search_type: str | None = None,
        alpha: float | None = None,
    ) -> Any | None:
        """
        Get cached query result.

        Args:
            query: Search query
            top_k: Number of results
            score_threshold: Minimum score threshold
            search_type: Type of search
            alpha: Hybrid search weight

        Returns:
            Cached result or None
        """
        key = self._make_key(query, top_k, score_threshold, search_type, alpha)
        return self.cache.get(key)

    def set(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        result: Any,
        search_type: str | None = None,
        alpha: float | None = None,
    ) -> None:
        """
        Cache query result.

        Args:
            query: Search query
            top_k: Number of results
            score_threshold: Minimum score threshold
            result: Query result to cache
            search_type: Type of search
            alpha: Hybrid search weight
        """
        key = self._make_key(query, top_k, score_threshold, search_type, alpha)
        self.cache.set(key, result)

    def clear(self) -> None:
        """Clear all cached queries."""
        self.cache.clear()
