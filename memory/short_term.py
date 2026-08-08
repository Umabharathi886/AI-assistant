"""
Module 11 — Short-Term Memory.

Wraps LangChain's in-memory chat history for the *current* conversation
turn window (fast, per-session, RAM only). Persisted history for reload
across app restarts is handled separately by memory/sqlite_memory.py.
"""
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

_SESSION_STORE: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = InMemoryChatMessageHistory()
    return _SESSION_STORE[session_id]


def add_turn(session_id: str, human_text: str, ai_text: str):
    history = get_session_history(session_id)
    history.add_message(HumanMessage(content=human_text))
    history.add_message(AIMessage(content=ai_text))


def get_recent_context(session_id: str, max_turns: int = 6) -> str:
    """Return the last N turns formatted as plain text for prompt injection."""
    history = get_session_history(session_id)
    messages = history.messages[-(max_turns * 2):]
    lines = []
    for m in messages:
        speaker = "Employee" if isinstance(m, HumanMessage) else "Assistant"
        lines.append(f"{speaker}: {m.content}")
    return "\n".join(lines)


def clear_session(session_id: str):
    _SESSION_STORE.pop(session_id, None)
