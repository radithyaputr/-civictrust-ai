"""
CivicTrust AI - RAG Pipeline Tests
Tests for embeddings, vector store, retriever, and ingestion.
"""
import pytest
import tempfile
import os
from app.config import settings
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.rag.retriever import RAGRetriever
from app.rag.ingestion import DocumentIngestion


@pytest.fixture
def temp_vector_store():
    """Create a vector store with temp path for testing."""
    original_path = settings.VECTOR_STORE_PATH
    with tempfile.TemporaryDirectory() as tmpdir:
        settings.VECTOR_STORE_PATH = tmpdir
        vs = VectorStore()
        yield vs
    settings.VECTOR_STORE_PATH = original_path


def test_embedding_generation():
    """Test that embeddings are generated correctly."""
    embedder = EmbeddingGenerator()
    embedding = embedder.embed("Test text for embedding")
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_embedding_dimension():
    """Test embedding dimension matches expected."""
    embedder = EmbeddingGenerator()
    embedding = embedder.embed("Test")
    assert len(embedding) == 384


def test_embedding_batch():
    """Test batch embedding generation."""
    embedder = EmbeddingGenerator()
    texts = ["Text one", "Text two", "Text three"]
    embeddings = embedder.embed_batch(texts)
    assert len(embeddings) == 3
    assert all(len(e) == 384 for e in embeddings)


def test_embedding_query():
    """Test query embedding."""
    embedder = EmbeddingGenerator()
    emb1 = embedder.embed("What is KTP?")
    emb2 = embedder.embed_query("What is KTP?")
    assert emb1 == emb2


@pytest.mark.asyncio
async def test_vector_store_add_and_search(temp_vector_store):
    """Test adding documents and searching."""
    vs = temp_vector_store
    await vs.add_document(
        doc_id="test-1",
        content="Pembuatan KTP membutuhkan Kartu Keluarga",
        source="https://dukcapil.go.id",
        source_type="government",
    )
    results = await vs.search("KTP", top_k=5)
    assert len(results) > 0
    assert results[0]["id"] == "test-1"
    assert results[0]["score"] > 0


@pytest.mark.asyncio
async def test_vector_store_search_empty(temp_vector_store):
    """Test search on empty vector store."""
    results = await temp_vector_store.search("test", top_k=5)
    assert results == []


@pytest.mark.asyncio
async def test_vector_store_delete(temp_vector_store):
    """Test deleting documents from vector store."""
    vs = temp_vector_store
    await vs.add_document("del-test", "Content to delete", "source", "general")
    assert vs.get_total_count() == 1
    await vs.delete_document("del-test")
    assert vs.get_total_count() == 0


@pytest.mark.asyncio
async def test_vector_store_reranking(temp_vector_store):
    """Test that reranking promotes credible sources."""
    vs = temp_vector_store
    await vs.add_document(
        "doc-low", "Low credibility content about public service",
        "unknown-blog.com", "general",
    )
    await vs.add_document(
        "doc-high", "High credibility content about public service",
        "kemenkes.go.id", "ministry",
    )
    results = await vs.search("public service", top_k=5)
    assert len(results) == 2
    assert "rerank_score" in results[0]


@pytest.mark.asyncio
async def test_retriever_search(temp_vector_store):
    """Test RAG retriever search."""
    await temp_vector_store.add_document(
        "rag-test", "Test content for retrieval",
        "test-source", "general",
    )
    retriever = RAGRetriever()
    retriever.vector_store = temp_vector_store
    results = await retriever.search("test content", top_k=5)
    assert len(results) > 0


@pytest.mark.asyncio
async def test_retriever_search_by_type(temp_vector_store):
    """Test retriever filters by source type."""
    await temp_vector_store.add_document(
        "doc1", "Health info", "kemkes.go.id", "ministry",
    )
    await temp_vector_store.add_document(
        "doc2", "News article", "news.com", "news",
    )
    retriever = RAGRetriever()
    retriever.vector_store = temp_vector_store
    results = await retriever.search_by_source_type("info", "ministry", top_k=5)
    assert len(results) == 1
    assert results[0]["source_type"] == "ministry"


@pytest.mark.asyncio
async def test_ingestion_chunking():
    """Test document chunking logic."""
    ingestion = DocumentIngestion()
    text = "word " * 2000
    chunks = ingestion._semantic_chunk(text)
    assert len(chunks) > 0
    assert all(len(c.split()) <= 512 for c in chunks)


@pytest.mark.asyncio
async def test_ingestion_paragraph_chunking():
    """Test semantic chunking preserves paragraphs."""
    ingestion = DocumentIngestion()
    text = "Paragraf pertama tentang KTP.\n\nParagraf kedua tentang KK.\n\nParagraf ketiga tentang Akta."
    chunks = ingestion._semantic_chunk(text)
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_ingestion_small_text():
    """Test ingestion with very small text."""
    ingestion = DocumentIngestion()
    chunks = ingestion._semantic_chunk("Pendek")
    assert len(chunks) == 1
    assert chunks[0] == "Pendek"


@pytest.mark.asyncio
async def test_vector_store_persistence(temp_vector_store):
    """Test vector store saves to disk."""
    vs = temp_vector_store
    await vs.add_document("persist-test", "Persist this content", "source", "general")
    assert os.path.exists(vs.index_path)
    assert os.path.exists(vs.metadata_path)