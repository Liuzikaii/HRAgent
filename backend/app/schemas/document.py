"""Pydantic schemas for document API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """A single document in the response."""
    id: UUID
    filename: str
    file_size: int
    chunk_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """List of uploaded documents."""
    documents: list[DocumentResponse]


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""
    id: UUID
    filename: str
    chunk_count: int
    status: str
    message: str
