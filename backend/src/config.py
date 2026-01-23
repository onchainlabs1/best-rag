"""Configuration using pydantic-settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/knowledgebase"
    storage_backend: Literal["sqlite", "postgresql"] = "sqlite"  # Default to SQLite for development

    # Vector Database
    chroma_path: str = "./data/chroma"

    # LLM Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    llm_provider: Literal["openai", "anthropic", "groq", "local"] = "groq"
    llm_model: str = "llama-3.1-8b-instant"  # Current Groq model (70b was decommissioned)

    # Embeddings
    embedding_provider: Literal["openai", "local"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "all-MiniLM-L6-v2"

    # LangSmith (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "rag-knowledge-base"

    # App Settings
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "*"  # Comma-separated list of allowed origins, or "*" for all

    # Performance Settings
    chroma_batch_size: int = 100
    embedding_batch_size_local: int = 64
    embedding_batch_size_openai: int = 2048

    # LLM Settings
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1000

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_queries: str = "10/minute"
    rate_limit_uploads: str = "5/minute"
    rate_limit_agents: str = "20/minute"

    # Search Configuration
    search_type: Literal["vector", "bm25", "hybrid"] = "vector"
    hybrid_search_alpha: float = 0.5  # 0.5 = 50% vector, 50% BM25

    # Re-ranking Configuration
    rerank_enabled: bool = False
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_top_k: int | None = None  # None = re-rank all results

    # Caching Configuration
    cache_enabled: bool = True
    cache_embeddings_ttl: int = 3600  # 1 hour
    cache_queries_ttl: int = 300  # 5 minutes

    # Query Expansion Configuration
    query_expansion_enabled: bool = False
    query_expansion_use_llm: bool = True

    # Checkpointing Configuration
    checkpointing_enabled: bool = False
    checkpoint_path: str = "./data/checkpoints"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
