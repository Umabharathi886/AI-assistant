"""
Module 4 — Email Agent tools.

Wraps LangChain's GmailToolkit when GMAIL_ENABLED=true and real OAuth
credentials are present at data/gmail_credentials.json. When Gmail is
not configured, falls back to a local "draft only" tool so the rest of
the app (and demo/grading) still works without live email access.

Gmail Setup (see README for full steps):
1. Create a Google Cloud project, enable the Gmail API.
2. Create OAuth Client ID (Desktop app), download as credentials.json.
3. Save it to data/gmail_credentials.json.
4. Set GMAIL_ENABLED=true in .env.
5. First run will open a browser window to authorize; token is cached
   to data/gmail_token.json.
"""
from langchain_core.tools import tool

from config import GMAIL_ENABLED, GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH


def _load_real_gmail_tools():
    from langchain_google_community import GmailToolkit  # noqa
    from langchain_google_community.gmail.utils import (
        build_resource_service,
        get_gmail_credentials,
    )

    credentials = get_gmail_credentials(
        token_file=GMAIL_TOKEN_PATH,
        scopes=["https://mail.google.com/"],
        client_secrets_file=GMAIL_CREDENTIALS_PATH,
    )
    api_resource = build_resource_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    return toolkit.get_tools()


@tool("draft_email", return_direct=False)
def draft_email(subject: str, body: str, recipient: str = "") -> str:
    """Draft a professional email (does not send). Use this to produce
    email text for the employee to review, e.g. a leave request email."""
    to_line = f"To: {recipient}\n" if recipient else ""
    return f"{to_line}Subject: {subject}\n\n{body}"


def get_email_tools():
    """Returns the list of tools the Email Agent should bind. Falls back
    to draft-only mode if Gmail isn't configured, so the app still runs."""
    if GMAIL_ENABLED:
        try:
            return _load_real_gmail_tools() + [draft_email]
        except Exception:
            # Credentials missing/invalid -> degrade gracefully
            return [draft_email]
    return [draft_email]


EMAIL_TOOLS = get_email_tools()
