"""
Module 4 — Email Agent.

Drafts professional emails, reads the inbox, summarizes recent emails,
and sends emails through Gmail (when GMAIL_ENABLED=true and credentials
are configured; otherwise operates in draft-only mode).
"""
from agents.base import build_agent, run_agent
from tools.gmail_tool import EMAIL_TOOLS
from config import GMAIL_ENABLED

SYSTEM_PROMPT = f"""You are the Email Agent for NovaTech Solutions.
You help employees draft professional emails, summarize recent inbox
messages, and (when Gmail access is enabled) send emails on request.

Gmail live access is currently {"ENABLED" if GMAIL_ENABLED else "DISABLED"}.
If it is disabled and the employee asks you to send or read real email,
explain that you can draft the email text for them to send manually,
and that an administrator needs to configure Gmail credentials to
enable live sending/reading.

When drafting, write clear, professional, courteous email copy with an
appropriate subject line. Match the employee's requested tone if given."""

_agent = None


def get_email_agent():
    global _agent
    if _agent is None:
        _agent = build_agent("Email_Agent", EMAIL_TOOLS, SYSTEM_PROMPT)
    return _agent


def handle_email_request(user_message: str, context: str = "") -> str:
    return run_agent(get_email_agent(), user_message, context)
