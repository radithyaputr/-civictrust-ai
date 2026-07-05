"""
CivicTrust AI - Retriever Agent
Retrieves relevant documents from the vector store.
"""
import logging
from typing import List, Dict, Any, Optional
from app.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)


class RetrieverAgent:
    """Agent for retrieving relevant documents."""

    def __init__(self):
        self.retriever = RAGRetriever()

    async def retrieve(
        self,
        query: str,
        plan: Optional[Dict] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for the query."""
        try:
            # Extract sub-questions from plan if available
            queries = [query]
            if plan and "sub_questions" in plan:
                queries.extend(plan["sub_questions"])

            all_docs = []
            seen_ids = set()

            for q in queries:
                docs = await self.retriever.search(q, top_k=top_k)
                for doc in docs:
                    doc_id = doc.get("id", "")
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        all_docs.append(doc)

            # Sort by relevance score
            all_docs.sort(key=lambda x: x.get("score", 0), reverse=True)
            return all_docs[:top_k]

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []