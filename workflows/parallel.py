"""
Module 8 — Parallel Processing.

Executes multiple independent research tasks simultaneously (e.g.
"Research Google, Microsoft, Amazon, and OpenAI") and combines them
into a single comparative report once every branch completes.

Implemented two ways for demonstration purposes:
1. ThreadPoolExecutor (see agents/research_agent.py) — used by default
   since LangChain tool-calling agents aren't natively async-safe here.
2. RunnableParallel — shown below for a small, fixed number of topics,
   satisfying the "Recommended LangChain Components" checklist.
"""
from langchain_core.runnables import RunnableParallel, RunnableLambda

from agents.research_agent import (
    research_multiple_topics_parallel,
    combine_research_findings,
)


def run_parallel_research(topics: list[str]) -> dict:
    """Primary entry point used by the app: thread-based parallel research
    (works for an arbitrary number of topics)."""
    findings = research_multiple_topics_parallel(topics)
    combined_report = combine_research_findings(findings)
    return {
        "topics": topics,
        "findings": [f.model_dump() for f in findings],
        "combined_report": combined_report,
    }


def build_fixed_parallel_chain(topics: list[str]) -> RunnableParallel:
    """Illustrates RunnableParallel explicitly for a fixed topic set, as
    called out in the capstone's recommended components list."""
    branches = {
        f"topic_{i}": RunnableLambda(lambda _x, t=t: research_multiple_topics_parallel([t])[0].summary)
        for i, t in enumerate(topics)
    }
    return RunnableParallel(**branches)
