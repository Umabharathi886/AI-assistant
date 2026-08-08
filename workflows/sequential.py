"""
Module 7 — Sequential Workflow.

Pipeline: User Request -> Research -> Summarize -> Generate Email
          -> Send Email -> Store Conversation

Used for multi-step requests like:
"Research Microsoft's latest AI products, summarize it, and email it to HR."
"""
from langchain_core.runnables import RunnableLambda, RunnableSequence

from agents.research_agent import handle_research_request
from agents.email_agent import handle_email_request
from agents.base import get_llm
from memory.sqlite_memory import SQLiteMemory

_memory = SQLiteMemory()


def _research_step(inputs: dict) -> dict:
    findings = handle_research_request(inputs["topic"])
    return {**inputs, "research": findings}


def _summarize_step(inputs: dict) -> dict:
    llm = get_llm(temperature=0.2)
    summary = llm.invoke(
        f"Summarize the following research into 3-5 concise bullet points "
        f"suitable for a business email:\n\n{inputs['research']}"
    ).content
    return {**inputs, "summary": summary}


def _generate_email_step(inputs: dict) -> dict:
    email_text = handle_email_request(
        f"Draft a professional email to {inputs.get('recipient', 'the team')} "
        f"with subject related to '{inputs['topic']}', using this summary as "
        f"the body content:\n\n{inputs['summary']}"
    )
    return {**inputs, "email_draft": email_text}


def _send_or_hold_step(inputs: dict) -> dict:
    # Sending is delegated to the Email Agent's own tools (Gmail toolkit or
    # draft-only fallback) — here we simply record the outcome.
    status = "Draft prepared (send manually)" if "Subject:" in inputs["email_draft"] else "Sent"
    return {**inputs, "send_status": status}


def _store_step(inputs: dict) -> dict:
    session_id = inputs.get("session_id", "default")
    _memory.add_message(session_id, "system", f"[Sequential Workflow] Topic: {inputs['topic']}", agent="Workflow")
    _memory.add_message(session_id, "assistant", inputs["email_draft"], agent="Email")
    return inputs


sequential_pipeline: RunnableSequence = (
    RunnableLambda(_research_step)
    | RunnableLambda(_summarize_step)
    | RunnableLambda(_generate_email_step)
    | RunnableLambda(_send_or_hold_step)
    | RunnableLambda(_store_step)
)


def run_sequential_workflow(topic: str, recipient: str = "", session_id: str = "default") -> dict:
    return sequential_pipeline.invoke({
        "topic": topic,
        "recipient": recipient,
        "session_id": session_id,
    })
