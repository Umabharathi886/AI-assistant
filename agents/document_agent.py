"""
Module 5 — Document Agent.

Searches uploaded documents, answers questions from PDFs, retrieves
company manuals, and explains company policies via ChromaDB. Distinct
from the HR Agent in scope: the Document Agent handles general
document / manual / SOP questions rather than only the seven core HR
policy areas.
"""
from agents.base import build_agent, run_agent
from tools.document_tool import DOCUMENT_TOOLS

SYSTEM_PROMPT = """You are the Document Agent for NovaTech Solutions.
You answer questions by searching the company's uploaded documents
(employee handbook, company guidelines, project documentation, SOPs,
manuals, and any other uploaded PDFs) using the search_company_documents
tool. Always search before answering. Quote or paraphrase the relevant
section, cite the source document, and clearly state if the requested
information isn't in the knowledge base."""

_agent = None


def get_document_agent():
    global _agent
    if _agent is None:
        _agent = build_agent("Document_Agent", DOCUMENT_TOOLS, SYSTEM_PROMPT)
    return _agent


def handle_document_request(user_message: str, context: str = "") -> str:
    return run_agent(get_document_agent(), user_message, context)
