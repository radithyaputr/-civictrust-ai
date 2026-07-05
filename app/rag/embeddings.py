"""
CivicTrust AI - Embeddings Module
Handles text embedding generation for the RAG pipeline.
"""
import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model = None

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not load {self.model_name}, using fallback: {e}")
                self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        self._load_model()
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        self._load_model()
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query."""
        return self.embed(query)