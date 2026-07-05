"""
CivicTrust AI - RAG Retriever
High-level retriever that wraps the vector store with async support.
"""
import logging
from typing import List, Dict, Any
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """High-level retriever for the RAG pipeline."""

    def __init__(self):
        self.vector_store = VectorStore()

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        try:
            return await self.vector_store.search(query, top_k=top_k)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def search_by_source_type(self, query: str, source_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search filtered by source type."""
        results = await self.vector_store.search(query, top_k=top_k * 3)
        return [r for r in results if r.get("source_type") == source_type][:top_k]