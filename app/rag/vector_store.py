"""
CivicTrust AI - Vector Store
FAISS-based vector store for document embeddings with async support.
"""
import asyncio
import logging
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from app.config import settings
from app.rag.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS vector store for document search with async-compatible operations."""

    def __init__(self):
        self.dimension = 384
        self.index_path = os.path.join(settings.VECTOR_STORE_PATH, "faiss.index")
        self.metadata_path = os.path.join(settings.VECTOR_STORE_PATH, "metadata.pkl")
        self.index = None
        self.metadata = []
        self._embedder = None
        self._lock = asyncio.Lock()

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = EmbeddingGenerator()
        return self._embedder

    def _ensure_loaded(self):
        if self.index is None:
            self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded FAISS index with {len(self.metadata)} documents")
            except Exception as e:
                logger.warning(f"Failed to load index, creating new: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        logger.info("Created new FAISS index")

    async def add_document(self, doc_id: str, content: str, source: str, source_type: str,
                           language: str = "id", metadata: Optional[Dict] = None):
        """Add a document to the vector store."""
        self._ensure_loaded()
        async with self._lock:
            embedding = self.embedder.embed(content)
            self.index.add(np.array([embedding], dtype=np.float32))
            self.metadata.append({
                "id": doc_id,
                "content": content,
                "source": source,
                "source_type": source_type,
                "language": language,
                "metadata": metadata or {},
            })
            await asyncio.to_thread(self._save)
            logger.info(f"Added document: {doc_id}")

    async def add_documents(self, documents: List[Dict[str, Any]]):
        """Add multiple documents to the vector store."""
        self._ensure_loaded()
        async with self._lock:
            texts = [doc["content"] for doc in documents]
            embeddings = self.embedder.embed_batch(texts)
            self.index.add(np.array(embeddings, dtype=np.float32))
            for i, doc in enumerate(documents):
                self.metadata.append({
                    "id": doc.get("id", f"doc_{len(self.metadata)}"),
                    "content": doc["content"],
                    "source": doc.get("source", "Unknown"),
                    "source_type": doc.get("source_type", "general"),
                    "language": doc.get("language", "id"),
                    "metadata": doc.get("metadata", {}),
                })
            await asyncio.to_thread(self._save)
            logger.info(f"Added {len(documents)} documents")

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        self._ensure_loaded()
        if self.index.ntotal == 0:
            return []

        query_embedding = self.embedder.embed_query(query)
        scores, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            min(top_k * 2, self.index.ntotal),
        )

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata) and scores[0][i] > 0:
                doc = dict(self.metadata[idx])
                doc["score"] = float(scores[0][i])
                results.append(doc)

        # Rerank: boost documents with higher source credibility
        results = self._rerank(results)

        return results[:top_k]

    def _rerank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results by combining semantic score with source credibility."""
        if not results:
            return results

        max_score = max(r["score"] for r in results) or 1.0

        source_credibility = {
            "law": 0.95, "regulation": 0.90, "ministry": 0.90,
            "government": 0.90, "who": 0.98, "un": 0.97,
            "university": 0.80, "news": 0.60, "general": 0.50,
        }

        for r in results:
            semantic_norm = r["score"] / max_score
            credibility = source_credibility.get(r.get("source_type", "general"), 0.5)
            r["rerank_score"] = (semantic_norm * 0.7) + (credibility * 0.3)

        results.sort(key=lambda x: x["rerank_score"], reverse=True)
        return results

    async def delete_document(self, doc_id: str):
        """Remove a document from the vector store."""
        self._ensure_loaded()
        async with self._lock:
            indices_to_remove = [
                i for i, m in enumerate(self.metadata) if m["id"] == doc_id
            ]
            if indices_to_remove:
                keep_indices = [i for i in range(len(self.metadata)) if i not in indices_to_remove]
                keep_metadata = [self.metadata[i] for i in keep_indices]
                self._create_new_index()
                if keep_metadata:
                    self.metadata = []
                    await self.add_documents(keep_metadata)
                logger.info(f"Deleted document: {doc_id}")

    def get_total_count(self) -> int:
        """Get total number of documents in the store."""
        return self.index.ntotal if self.index else 0

    def _save(self):
        """Save index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)