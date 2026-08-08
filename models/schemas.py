"""
Module 12 — Structured Outputs.

Pydantic models used to validate the structured reports every agent
ultimately produces, plus supporting models for routing and memory.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class Department(str, Enum):
    HR = "HR"
    OPERATIONS = "Operations"
    FINANCE = "Finance"
    IT_SUPPORT = "IT Support"
    ADMINISTRATION = "Administration"
    GENERAL = "General"


class AgentReport(BaseModel):
    """The standard structured report format required by Module 12."""

    task_summary: str = Field(..., description="One or two sentence summary of the task performed")
    department: Department = Field(..., description="Department this task belongs to")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority of the request")
    actions_taken: List[str] = Field(default_factory=list, description="Concrete actions the agent(s) performed")
    pending_actions: List[str] = Field(default_factory=list, description="Actions still outstanding")
    recommended_next_steps: List[str] = Field(default_factory=list, description="Suggested follow-ups for the employee")

    def to_markdown(self) -> str:
        def bullets(items: List[str]) -> str:
            return "\n".join(f"- {i}" for i in items) if items else "- None"

        return (
            f"### Task Summary\n{self.task_summary}\n\n"
            f"### Department\n{self.department.value}\n\n"
            f"### Priority\n{self.priority.value}\n\n"
            f"### Actions Taken\n{bullets(self.actions_taken)}\n\n"
            f"### Pending Actions\n{bullets(self.pending_actions)}\n\n"
            f"### Recommended Next Steps\n{bullets(self.recommended_next_steps)}\n"
        )


class RouteDecision(BaseModel):
    """Output of the Coordinator Agent's routing decision (Module 6 / 9)."""

    agent: str = Field(..., description="One of HR, RESEARCH, EMAIL, DOCUMENT, GENERAL")
    reasoning: str = Field(..., description="Brief reasoning for why this agent was chosen")
    sub_tasks: List[str] = Field(default_factory=list, description="Ordered sub-tasks if the request spans multiple agents")


class EmployeeProfile(BaseModel):
    """Long-term memory record for an employee (Module 11)."""

    employee_name: Optional[str] = None
    department: Optional[str] = None
    preferred_email_style: Optional[str] = None
    frequently_asked_questions: List[str] = Field(default_factory=list)
    frequently_accessed_documents: List[str] = Field(default_factory=list)


class ResearchFinding(BaseModel):
    """Single-source result used by parallel research (Module 8)."""

    source: str
    query: str
    summary: str
