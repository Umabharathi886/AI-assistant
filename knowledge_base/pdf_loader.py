"""
Module 10 — Company Knowledge Base: PDF Loader + Text Splitter.

Loads PDFs / plain text files uploaded via the Streamlit sidebar and
splits them into overlapping chunks ready for embedding into ChromaDB.
"""
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import CHUNK_SIZE, CHUNK_OVERLAP


def load_file(file_path: str) -> List[Document]:
    """Load a single PDF or TXT file into LangChain Documents."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(path))
    else:
        loader = TextLoader(str(path), encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata["source"] = path.name
    return docs


def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def load_and_split(file_path: str) -> List[Document]:
    return split_documents(load_file(file_path))
