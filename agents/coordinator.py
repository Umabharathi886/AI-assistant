"""
Module 6 — Coordinator Agent.
Module 9 — Conditional Routing (RunnableBranch).

The Coordinator classifies each employee request into one of:
    HR | RESEARCH | EMAIL | DOCUMENT | GENERAL
and routes it to the matching specialized agent. It also detects
multi-part requests (e.g. "get the leave policy AND draft an email
AND save it") and, in that case, hands off to the sequential workflow
instead of a single agent.
"""
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import get_llm
from agents.hr_agent import handle_hr_request
from agents.research_agent import handle_research_request
from agents.email_agent import handle_email_request
from agents.document_agent import handle_document_request
from models.schemas import RouteDecision

_parser = PydanticOutputParser(pydantic_object=RouteDecision)

_ROUTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the routing coordinator for an enterprise AI assistant with "
     "four specialist agents:\n"
     "- HR: leave/attendance/WFH/holiday/benefits/joining/exit policy questions\n"
     "- RESEARCH: external/internet research, industry news, competitor info\n"
     "- EMAIL: drafting, reading, summarizing, or sending emails\n"
     "- DOCUMENT: questions about uploaded manuals, SOPs, handbooks, project docs\n"
     "If the request doesn't fit any specialist, choose GENERAL.\n"
     "If the request has multiple distinct steps spanning agents (e.g. "
     "'research X, summarize it, and email it'), list them in order in "
     "sub_tasks, and set agent to the FIRST agent needed.\n\n"
     "{format_instructions}"),
    ("human", "{request}"),
]).partial(format_instructions=_parser.get_format_instructions())


def classify_request(user_message: str) -> RouteDecision:
    llm = get_llm(temperature=0)
    chain = _ROUTING_PROMPT | llm | _parser
    try:
        return chain.invoke({"request": user_message})
    except Exception:
        # Safe fallback if the model output doesn't parse cleanly
        return RouteDecision(agent="GENERAL", reasoning="Fallback: could not parse routing decision.", sub_tasks=[])


def _general_response(user_message: str, context: str = "") -> str:
    llm = get_llm(temperature=0.3)
    prompt = (
        "You are the general-purpose assistant for the Enterprise Operations "
        "AI Assistant. Answer helpfully and concisely. If this really belongs "
        "to HR, Research, Email, or Document handling, say so.\n\n"
        f"{context}\n\nEmployee request: {user_message}"
    )
    return llm.invoke(prompt).content


# ---------------------------------------------------------------------------
# Module 9 — RunnableBranch conditional routing
# ---------------------------------------------------------------------------
def _is_agent(name: str):
    return lambda x: x["route"].agent == name


route_branch = RunnableBranch(
    (_is_agent("HR"), RunnableLambda(lambda x: handle_hr_request(x["request"], x.get("context", "")))),
    (_is_agent("RESEARCH"), RunnableLambda(lambda x: handle_research_request(x["request"], x.get("context", "")))),
    (_is_agent("EMAIL"), RunnableLambda(lambda x: handle_email_request(x["request"], x.get("context", "")))),
    (_is_agent("DOCUMENT"), RunnableLambda(lambda x: handle_document_request(x["request"], x.get("context", "")))),
    RunnableLambda(lambda x: _general_response(x["request"], x.get("context", ""))),  # default -> GENERAL
)


def route_and_respond(user_message: str, context: str = "") -> dict:
    """Classify the request, route it through RunnableBranch, and return
    both the routing decision and the agent's response."""
    decision = classify_request(user_message)
    response = route_branch.invoke({
        "route": decision,
        "request": user_message,
        "context": context,
    })
    return {"decision": decision, "response": response}


AGENT_DISPATCH = {
    "HR": handle_hr_request,
    "RESEARCH": handle_research_request,
    "EMAIL": handle_email_request,
    "DOCUMENT": handle_document_request,
    "GENERAL": _general_response,
}
