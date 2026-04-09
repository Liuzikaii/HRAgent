"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── DeepSeek LLM ───
    deepseek_api_key: str = ""

    # ─── Database ───
    database_url: str = "postgresql+asyncpg://hragent:hragent123@postgres:5432/hragent"

    # ─── Milvus ───
    milvus_host: str = "milvus"
    milvus_port: int = 19530
    milvus_collection: str = "hr_documents"

    # ─── Embedding ───
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dimension: int = 512

    # ─── RAG ───
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    # ─── App ───
    app_env: str = "production"
    log_level: str = "info"

    model_config = {"env_file": ".env", "extra": "allow"}


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
