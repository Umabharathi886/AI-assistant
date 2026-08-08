"""
Module 10 — Company Knowledge Base: ChromaDB.

Owns the single persistent Chroma collection ("company_knowledge_base")
that the HR Agent and Document Agent both query through
knowledge_base/retriever.py.

Embeddings are provided locally via sentence-transformers by default
(EMBEDDING_PROVIDER="huggingface" in config.py) so the knowledge base
works completely free, with no API key required. Set
EMBEDDING_PROVIDER=openai in .env to use OpenAI embeddings instead.
"""
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_PROVIDER,
    HF_EMBEDDING_MODEL,
    OPENAI_API_KEY,
)

_vectorstore: Optional[Chroma] = None


def get_embeddings():
    if EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    # default: local, free, no API key needed
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=HF_EMBEDDING_MODEL)


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_PERSIST_DIR,
        )
    return _vectorstore


def add_documents(documents: List[Document]) -> int:
    """Embed and add document chunks to the persistent store. Returns count added."""
    if not documents:
        return 0
    store = get_vectorstore()
    store.add_documents(documents)
    return len(documents)


def list_sources() -> List[str]:
    """Return the distinct source filenames currently indexed."""
    store = get_vectorstore()
    try:
        data = store.get(include=["metadatas"])
        sources = {m.get("source", "unknown") for m in data.get("metadatas", []) if m}
        return sorted(sources)
    except Exception:
        return []


def reset_knowledge_base():
    global _vectorstore
    store = get_vectorstore()
    store.delete_collection()
    _vectorstore = None
