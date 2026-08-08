"""
Module 10 — Company Knowledge Base: Retriever.

Shared retrieval interface used by both the HR Agent (policy questions)
and the Document Agent (general document Q&A). Kept separate so each
agent can apply its own metadata filters / top-k in the future.
"""
from typing import List, Dict, Any

from config import RETRIEVER_TOP_K
from knowledge_base.chroma_setup import get_vectorstore


def retrieve(query: str, k: int = RETRIEVER_TOP_K) -> List[Dict[str, Any]]:
    store = get_vectorstore()
    results = store.similarity_search_with_relevance_scores(query, k=k)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "score": score,
        }
        for doc, score in results
    ]


def retrieve_as_context(query: str, k: int = RETRIEVER_TOP_K) -> str:
    """Formatted context block ready to inject into an LLM prompt."""
    results = retrieve(query, k=k)
    if not results:
        return "No relevant documents found in the knowledge base."
    blocks = []
    for r in results:
        page_info = f" (page {r['page']})" if r.get("page") is not None else ""
        blocks.append(f"[Source: {r['source']}{page_info}]\n{r['content']}")
    return "\n\n---\n\n".join(blocks)
