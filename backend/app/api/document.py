"""Document management API routes."""

import logging
import os
import tempfile
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentUploadResponse
from app.services.embedding import embed_texts
from app.services.milvus_client import delete_by_document_id, insert_vectors
from app.utils.pdf_parser import parse_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and process an HR document (PDF, Markdown, or TXT)."""
    # Validate file extension
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}。支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save to temp file
    content = await file.read()
    file_size = len(content)

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    # Create document record
    doc = Document(filename=filename, file_size=file_size, status="processing")
    db.add(doc)
    await db.flush()

    try:
        # Parse and chunk the document
        chunks = parse_file(tmp_path)

        # Generate embeddings
        embeddings = embed_texts(chunks)

        # Insert into Milvus
        insert_vectors(str(doc.id), chunks, embeddings)

        # Update document status
        doc.chunk_count = len(chunks)
        doc.status = "ready"
        await db.flush()

        logger.info(f"Document '{filename}' processed: {len(chunks)} chunks")

        return DocumentUploadResponse(
            id=doc.id,
            filename=filename,
            chunk_count=len(chunks),
            status="ready",
            message=f"文档 '{filename}' 上传成功，已解析为 {len(chunks)} 个文本片段",
        )

    except Exception as e:
        doc.status = "error"
        await db.flush()
        logger.error(f"Error processing document '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

    finally:
        os.unlink(tmp_path)


@router.get("", response_model=DocumentListResponse)
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all uploaded documents."""
    query = select(Document).order_by(Document.created_at.desc())
    result = await db.execute(query)
    documents = result.scalars().all()
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents]
    )


@router.delete("/{document_id}")
async def delete_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a document and its vectors from Milvus."""
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete vectors from Milvus
    try:
        delete_by_document_id(str(document_id))
    except Exception as e:
        logger.error(f"Error deleting vectors: {e}")

    await db.delete(doc)
    return {"message": f"文档 '{doc.filename}' 已删除"}
