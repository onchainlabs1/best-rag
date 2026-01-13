"""Embedding generation service."""

import os
from typing import List
import structlog
from src.schemas.rag import EmbeddingRequest, EmbeddingResponse
from src.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating embeddings from text."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        """
        Initialize embedding service.

        Args:
            provider: Embedding provider ('openai' or 'local')
            model: Model name to use
        """
        self.provider = provider or settings.embedding_provider
        self.model = model or (
            settings.embedding_model
            if self.provider == "openai"
            else settings.local_embedding_model
        )

        if self.provider == "local":
            self._init_local_model()
        elif self.provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def _init_local_model(self) -> None:
        """Initialize local sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("loading_embedding_model", model=self.model)
            
            # Use a faster, smaller model if available
            # all-MiniLM-L6-v2 is already fast, but we can optimize loading
            self.model_instance = SentenceTransformer(
                self.model,
                device='cpu',  # Explicit CPU (can change to 'cuda' if GPU available)
            )
            self.dimensions = self.model_instance.get_sentence_embedding_dimension()
            logger.info("embedding_model_loaded", dimensions=self.dimensions)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for local embeddings. "
                "Install with: pip install sentence-transformers"
            )

    def _init_openai(self) -> None:
        """Initialize OpenAI embeddings."""
        try:
            from openai import OpenAI

            api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

            self.client = OpenAI(api_key=api_key)
            # Default dimensions for OpenAI models
            self.dimensions = 1536 if "3-small" in self.model else 3072
        except ImportError:
            raise ImportError(
                "openai package is required for OpenAI embeddings. "
                "Install with: pip install openai"
            )

    def generate_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate embeddings for a list of texts.

        Args:
            request: Embedding request with texts and optional model

        Returns:
            Embedding response with embeddings and metadata
        """
        model = request.model or self.model

        if self.provider == "local":
            embeddings = self._generate_local(request.texts, model)
        elif self.provider == "openai":
            embeddings = self._generate_openai(request.texts, model)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            dimensions=len(embeddings[0]) if embeddings else 0,
        )

    def _generate_local(self, texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers model."""
        # Use larger batch size for better performance (sentence-transformers handles this well)
        # Process all at once if possible, otherwise in batches
        batch_size = 64  # Increased for better performance
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model_instance.encode(
                batch,
                batch_size=len(batch),
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
                device='cpu',  # Explicit device
            )
            all_embeddings.extend(batch_embeddings.tolist())
        
        return all_embeddings

    def _generate_openai(self, texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        # OpenAI API accepts up to 2048 inputs per request
        all_embeddings: List[List[float]] = []
        batch_size = 2048

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(
                model=model,
                input=batch,
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (convenience method).

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        request = EmbeddingRequest(texts=[text])
        response = self.generate_embeddings(request)
        return response.embeddings[0]
