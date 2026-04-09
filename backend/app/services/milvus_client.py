"""Milvus vector database client."""

import logging
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

_collection = None


def connect_milvus():
    """Establish connection to Milvus."""
    settings = get_settings()
    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=settings.milvus_port,
    )
    logger.info(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")


def get_collection() -> Collection:
    """Get or create the HR documents collection."""
    global _collection
    if _collection is not None:
        return _collection

    settings = get_settings()
    collection_name = settings.milvus_collection

    if not utility.has_collection(collection_name):
        logger.info(f"Creating Milvus collection: {collection_name}")
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.embedding_dimension),
        ]
        schema = CollectionSchema(fields=fields, description="HR document chunks")
        _collection = Collection(name=collection_name, schema=schema)

        # Create IVF_FLAT index for search
        index_params = {
            "metric_type": "IP",  # Inner Product for normalized embeddings
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        _collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"Collection '{collection_name}' created with IVF_FLAT index")
    else:
        _collection = Collection(name=collection_name)

    _collection.load()
    return _collection


def insert_vectors(document_id: str, texts: list[str], embeddings: list[list[float]]) -> int:
    """Insert document chunks and their embeddings into Milvus.

    Returns the number of inserted vectors.
    """
    collection = get_collection()
    data = [
        [document_id] * len(texts),        # document_id
        list(range(len(texts))),             # chunk_index
        texts,                               # text
        embeddings,                          # embedding vectors
    ]
    result = collection.insert(data)
    collection.flush()
    logger.info(f"Inserted {len(texts)} vectors for document {document_id}")
    return result.insert_count


def search_vectors(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """Search for similar vectors and return matched text chunks.

    Returns a list of dicts with keys: text, score, document_id, chunk_index.
    """
    collection = get_collection()
    search_params = {"metric_type": "IP", "params": {"nprobe": 16}}

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["text", "document_id", "chunk_index"],
    )

    matches = []
    for hit in results[0]:
        matches.append({
            "text": hit.entity.get("text"),
            "score": hit.score,
            "document_id": hit.entity.get("document_id"),
            "chunk_index": hit.entity.get("chunk_index"),
        })
    return matches


def delete_by_document_id(document_id: str):
    """Delete all vectors belonging to a specific document."""
    collection = get_collection()
    expr = f'document_id == "{document_id}"'
    collection.delete(expr)
    collection.flush()
    logger.info(f"Deleted vectors for document {document_id}")
