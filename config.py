"""
Central configuration for the Enterprise Operations AI Assistant.
Loads environment variables and exposes shared paths / constants used
across agents, tools, memory, and the knowledge base.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DOCS_DIR = BASE_DIR / "sample_documents"

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma_db"))
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "memory.db"))
GMAIL_CREDENTIALS_PATH = str(DATA_DIR / "gmail_credentials.json")
GMAIL_TOKEN_PATH = str(DATA_DIR / "gmail_token.json")

DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# LLM / API config
# ---------------------------------------------------------------------------
# LLM_PROVIDER: "groq" (free, default) or "openai" (paid)

# ---------------------------------------------------------------------------
# LLM / API config
# ---------------------------------------------------------------------------

def get_secret(name, default=""):
    """Read from Streamlit Secrets when available, otherwise use environment variables."""
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


LLM_PROVIDER = get_secret("LLM_PROVIDER", "groq").lower()

GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
GROQ_MODEL = get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")

OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "")
OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")

# ---------------------------------------------------------------------------
# Embeddings config (ChromaDB) — local, free, no API key required
# ---------------------------------------------------------------------------
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface").lower()
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

GMAIL_ENABLED = os.getenv("GMAIL_ENABLED", "false").lower() == "true"
GDRIVE_ENABLED = os.getenv("GDRIVE_ENABLED", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Agent / routing constants
# ---------------------------------------------------------------------------
AGENT_NAMES = ["HR", "RESEARCH", "EMAIL", "DOCUMENT", "GENERAL"]

DEPARTMENTS = [
    "HR",
    "Operations",
    "Finance",
    "IT Support",
    "Administration",
]

CHROMA_COLLECTION_NAME = "company_knowledge_base"

# Text splitting defaults (Module 10)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Retrieval defaults
RETRIEVER_TOP_K = 4
