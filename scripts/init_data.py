"""Initialize sample HR data into the system.

Usage (from within the backend container):
    python /app/scripts/init_data.py
"""

import os
import sys
from pathlib import Path

# Add the backend app to the Python path
sys.path.insert(0, "/app")

from app.config import get_settings
from app.services.embedding import embed_texts
from app.services.milvus_client import connect_milvus, get_collection, insert_vectors
from app.utils.pdf_parser import parse_file


SAMPLE_DATA_DIR = Path("/app/data/sample")


def init_sample_data():
    """Load and index all sample HR documents."""
    settings = get_settings()

    # Connect to Milvus
    print("Connecting to Milvus...")
    connect_milvus()
    get_collection()

    # Find all sample files
    sample_files = list(SAMPLE_DATA_DIR.glob("*.md")) + list(SAMPLE_DATA_DIR.glob("*.txt")) + list(SAMPLE_DATA_DIR.glob("*.pdf"))

    if not sample_files:
        print(f"No sample files found in {SAMPLE_DATA_DIR}")
        return

    print(f"Found {len(sample_files)} sample files:")

    for file_path in sample_files:
        print(f"\n{'=' * 50}")
        print(f"Processing: {file_path.name}")

        try:
            # Parse and chunk
            chunks = parse_file(file_path)
            print(f"  Chunks: {len(chunks)}")

            # Generate embeddings
            print(f"  Generating embeddings...")
            embeddings = embed_texts(chunks)
            print(f"  Embeddings: {len(embeddings)} vectors of dim {len(embeddings[0])}")

            # Insert into Milvus
            doc_id = file_path.stem  # Use filename as document ID
            count = insert_vectors(doc_id, chunks, embeddings)
            print(f"  Inserted: {count} vectors")

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'=' * 50}")
    print("Sample data initialization complete!")


if __name__ == "__main__":
    init_sample_data()
