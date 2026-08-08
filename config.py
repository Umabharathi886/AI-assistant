"""
Central configuration for the Enterprise Operations AI Assistant.
Loads environment variables and exposes shared paths / constants used
across agents, tools, memory, and the knowledge base.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

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
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
