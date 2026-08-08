"""
Orchestration layer that ties together:
- Module 6/9: Coordinator routing (RunnableBranch)
- Module 11: Short-term + long-term memory
- Module 12: Structured Pydantic report generation

This is the single function the Streamlit app calls per chat turn.
"""
from typing import Dict, Any

from agents.coordinator import route_and_respond
from memory import short_term, long_term
from memory.sqlite_memory import SQLiteMemory
from utils.report_generator import generate_structured_report

_memory = SQLiteMemory()


def process_employee_request(user_message: str, session_id: str = "default") -> Dict[str, Any]:
    # 1. Long-term memory: capture "remember that..." style facts
    long_term.maybe_extract_and_store(session_id, user_message)
    long_term.record_question(session_id, user_message)

    # 2. Short-term context for the current session
    context = short_term.get_recent_context(session_id)
    profile_context = long_term.profile_context_string(session_id)
    full_context = f"Known employee context:\n{profile_context}\n\nRecent conversation:\n{context}"

    # 3. Route + execute via Coordinator Agent / RunnableBranch
    result = route_and_respond(user_message, full_context)
    decision = result["decision"]
    response_text = result["response"]

    # 4. Structured output (Module 12)
    report = generate_structured_report(
        user_message=user_message,
        agent_name=decision.agent,
        response_text=response_text,
    )

    # 5. Persist memory
    short_term.add_turn(session_id, user_message, response_text)
    _memory.add_message(session_id, "user", user_message)
    _memory.add_message(session_id, "assistant", response_text, agent=decision.agent)

    return {
        "agent": decision.agent,
        "reasoning": decision.reasoning,
        "sub_tasks": decision.sub_tasks,
        "response": response_text,
        "report": report,
    }
