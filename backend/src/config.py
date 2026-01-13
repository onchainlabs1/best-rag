"""Configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/knowledgebase"

    # Vector Database
    chroma_path: str = "./data/chroma"

    # LLM Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    llm_provider: Literal["openai", "anthropic", "groq", "local"] = "groq"
    llm_model: str = "llama-3.1-8b-instant"  # Modelo atual do Groq (70b foi descontinuado)

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
