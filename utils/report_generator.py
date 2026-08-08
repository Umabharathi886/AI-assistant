"""
Module 12 — Structured Outputs.

Turns a raw agent response into the required structured report format:
Task Summary, Department, Priority, Actions Taken, Pending Actions,
Recommended Next Steps — validated with the AgentReport Pydantic model.
"""
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import get_llm
from models.schemas import AgentReport

_AGENT_TO_DEPARTMENT = {
    "HR": "HR",
    "RESEARCH": "Operations",
    "EMAIL": "Administration",
    "DOCUMENT": "Operations",
    "GENERAL": "General",
}

_parser = PydanticOutputParser(pydantic_object=AgentReport)

_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You convert an AI agent's response into a structured business report. "
     "Be factual and concise -- base actions_taken strictly on what the "
     "response says was done. department must be one of: HR, Operations, "
     "Finance, IT Support, Administration, General; use this hint if unsure: "
     "{department_hint}.\n\n{format_instructions}"),
    ("human", "Original request: {request}\n\nAgent ({agent_name}) response:\n{response}"),
]).partial(format_instructions=_parser.get_format_instructions())


def generate_structured_report(user_message: str, agent_name: str, response_text: str) -> AgentReport:
    llm = get_llm(temperature=0)
    chain = _PROMPT | llm | _parser
    hint = _AGENT_TO_DEPARTMENT.get(agent_name, "General")
    try:
        return chain.invoke({
            "request": user_message,
            "agent_name": agent_name,
            "response": response_text,
            "department_hint": hint,
        })
    except Exception:
        # Fallback minimal valid report if structured parsing fails
        valid_departments = {"HR", "Operations", "Finance", "IT Support", "Administration", "General"}
        return AgentReport(
            task_summary=user_message[:200],
            department=hint if hint in valid_departments else "General",
            actions_taken=[f"{agent_name} agent responded to the request."],
        )
