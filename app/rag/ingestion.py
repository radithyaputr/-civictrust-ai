"""
CivicTrust AI - Document Ingestion
Handles document processing and ingestion into the vector store with semantic chunking.
"""
import logging
import re
from typing import List, Dict, Optional
from app.rag.vector_store import VectorStore
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentIngestion:
    """Document ingestion pipeline with semantic chunking."""

    def __init__(self):
        self.vector_store = VectorStore()

    async def ingest(
        self,
        document_id: str,
        content: str,
        source: str,
        source_type: str,
        language: str = "id",
        metadata: Optional[Dict] = None,
    ):
        """Ingest a document into the vector store."""
        chunks = self._semantic_chunk(content)

        documents = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            documents.append({
                "id": chunk_id,
                "content": chunk,
                "source": source,
                "source_type": source_type,
                "language": language,
                "metadata": {
                    **(metadata or {}),
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            })

        await self.vector_store.add_documents(documents)
        logger.info(f"Ingested {len(chunks)} chunks from {document_id}")

    def _semantic_chunk(self, text: str) -> List[str]:
        """Split text into semantically meaningful chunks."""
        max_chunk = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP

        # Try splitting by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []

        for para in paragraphs:
            para_words = para.split()
            current_words = sum(len(c.split()) for c in current_chunk)

            if current_words + len(para_words) <= max_chunk:
                current_chunk.append(para)
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                # If a single paragraph exceeds max_chunk, split it
                if len(para_words) > max_chunk:
                    for i in range(0, len(para_words), max_chunk - overlap):
                        sub = " ".join(para_words[i:i + max_chunk])
                        if sub:
                            chunks.append(sub)
                else:
                    current_chunk = [para]

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks if chunks else [text]