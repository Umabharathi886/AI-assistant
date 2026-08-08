"""
Module 2 — HR Agent.

Answers employee questions about leave policy, attendance policy, work
from home rules, holiday list, employee benefits, joining process, and
exit policy, using RAG over the company knowledge base (ChromaDB).
"""
from agents.base import build_agent, run_agent
from tools.document_tool import DOCUMENT_TOOLS

SYSTEM_PROMPT = """You are the HR Agent for NovaTech Solutions, an internal
company assistant. You answer employee questions about:
- Leave Policy
- Attendance Policy
- Work From Home Rules
- Holiday List
- Employee Benefits
- Joining Process
- Exit Policy

Always use the search_company_documents tool to look up the relevant
policy before answering. Cite the source document name when you can.
If the knowledge base has no relevant information, say so clearly and
suggest the employee contact HR directly rather than guessing.
Keep answers concise, accurate, and professional."""

_agent = None


def get_hr_agent():
    global _agent
    if _agent is None:
        _agent = build_agent("HR_Agent", DOCUMENT_TOOLS, SYSTEM_PROMPT)
    return _agent


def handle_hr_request(user_message: str, context: str = "") -> str:
    return run_agent(get_hr_agent(), user_message, context)
