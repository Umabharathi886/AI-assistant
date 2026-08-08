"""
Module 11 — Long-Term Memory.

Thin convenience layer over SQLiteMemory specifically for the kind of
durable facts the capstone spec calls out: employee name, department,
frequently asked questions, preferred email style, frequently accessed
documents. Also does simple keyword extraction so the Coordinator can
auto-detect "remember that ..." style statements (Scenario 3 / 4).
"""
import re
from typing import Optional

from memory.sqlite_memory import SQLiteMemory
from models.schemas import EmployeeProfile

_memory = SQLiteMemory()

_DEPT_PATTERN = re.compile(
    r"\b(?:i (?:belong to|am in|work in|am part of) the )?"
    r"(HR|Human Resources|Operations|Finance|IT Support|IT|Administration)\b",
    re.IGNORECASE,
)
_NAME_PATTERN = re.compile(r"\bmy name is ([A-Za-z][A-Za-z .'-]{1,40})", re.IGNORECASE)


def maybe_extract_and_store(session_id: str, user_text: str):
    """Look for statements like 'Remember that I belong to Finance' or
    'My name is Priya' and persist them to long-term memory."""
    name_match = _NAME_PATTERN.search(user_text)
    if name_match:
        _memory.update_profile(session_id, employee_name=name_match.group(1).strip())

    if "remember" in user_text.lower() or "belong to" in user_text.lower() or "department" in user_text.lower():
        dept_match = _DEPT_PATTERN.search(user_text)
        if dept_match:
            dept = dept_match.group(1)
            normalized = "IT Support" if dept.lower() in ("it", "it support") else dept.title()
            if normalized.lower() == "human resources":
                normalized = "HR"
            _memory.update_profile(session_id, department=normalized)


def record_question(session_id: str, question: str):
    _memory.update_profile(session_id, frequently_asked_questions=question)


def record_document_access(session_id: str, doc_name: str):
    _memory.update_profile(session_id, frequently_accessed_documents=doc_name)


def get_profile(session_id: str) -> EmployeeProfile:
    return _memory.get_profile(session_id)


def profile_context_string(session_id: str) -> str:
    """Human-readable snippet to inject into prompts so agents are aware
    of who the employee is (Scenario 4: 'What department do I belong to?')."""
    profile = get_profile(session_id)
    parts = []
    if profile.employee_name:
        parts.append(f"Employee name: {profile.employee_name}")
    if profile.department:
        parts.append(f"Department: {profile.department}")
    if profile.preferred_email_style:
        parts.append(f"Preferred email style: {profile.preferred_email_style}")
    if profile.frequently_asked_questions:
        parts.append("Frequently asked: " + "; ".join(profile.frequently_asked_questions[-5:]))
    return "\n".join(parts) if parts else "No long-term profile information stored yet."
