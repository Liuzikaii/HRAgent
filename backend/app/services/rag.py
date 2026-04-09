"""RAG retrieval service — query → embedding → Milvus search → context."""

import logging

from app.config import get_settings
from app.services.embedding import embed_query
from app.services.milvus_client import search_vectors

logger = logging.getLogger(__name__)


def retrieve_context(query: str) -> str:
    """Retrieve relevant document chunks for a given query.

    Returns a formatted string of the top-K most relevant text chunks.
    """
    settings = get_settings()

    # 1. Embed the query
    query_vector = embed_query(query)

    # 2. Search Milvus for similar chunks
    results = search_vectors(query_vector, top_k=settings.top_k)

    if not results:
        logger.info("No relevant documents found for query")
        return ""

    # 3. Format context from search results
    context_parts = []
    for i, match in enumerate(results, 1):
        score = match["score"]
        text = match["text"]
        context_parts.append(f"[参考文档片段 {i}] (相关度: {score:.3f})\n{text}")

    context = "\n\n".join(context_parts)
    logger.info(f"Retrieved {len(results)} chunks for query (top score: {results[0]['score']:.3f})")
    return context
