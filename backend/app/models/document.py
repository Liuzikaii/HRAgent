"""Document metadata database model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Document(Base):
    """Represents an uploaded HR document's metadata."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default="processing")  # processing, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)
