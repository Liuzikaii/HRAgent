"""Embedding service using BAAI/bge-small-zh-v1.5."""

import logging
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from app.config import get_settings

logger = logging.getLogger(__name__)

_embeddings = None


def get_embeddings() -> HuggingFaceBgeEmbeddings:
    """Get or create the singleton embedding model instance."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embeddings = HuggingFaceBgeEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embedding model loaded successfully")
    return _embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts into vectors."""
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)


def embed_query(text: str) -> list[float]:
    """Embed a single query text into a vector."""
    embeddings = get_embeddings()
    return embeddings.embed_query(text)
