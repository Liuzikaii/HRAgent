"""PDF parsing and text chunking utility."""

import logging
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract all text content from a PDF file."""
    reader = PdfReader(str(file_path))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text.strip())
    full_text = "\n\n".join(texts)
    logger.info(f"Extracted {len(full_text)} characters from {file_path}")
    return full_text


def extract_text_from_markdown(file_path: str | Path) -> str:
    """Extract text content from a Markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    logger.info(f"Read {len(text)} characters from {file_path}")
    return text


def split_text(text: str) -> list[str]:
    """Split text into chunks using RecursiveCharacterTextSplitter."""
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} chunks (chunk_size={settings.chunk_size})")
    return chunks


def parse_file(file_path: str | Path) -> list[str]:
    """Parse a file (PDF or Markdown) and return text chunks."""
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif suffix in (".md", ".txt"):
        text = extract_text_from_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    if not text.strip():
        raise ValueError(f"No text content extracted from {file_path}")

    return split_text(text)
