"""
Module 3 — Research Agent.

Performs external research using internet search and Wikipedia,
collecting and summarizing information from multiple online sources.
Also exposes a parallel multi-topic research helper for Module 8.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from agents.base import build_agent, run_agent, get_llm
from tools.search_tool import RESEARCH_TOOLS
from models.schemas import ResearchFinding

SYSTEM_PROMPT = """You are the Research Agent for NovaTech Solutions.
You research external, real-world information using the web_search and
wikipedia_search tools -- e.g. company news, AI product announcements,
industry trends. Always use at least one tool before answering unless
the question is trivial. Summarize findings clearly, note which source
each fact came from, and keep the summary focused and well-organized
(use short paragraphs or bullet points)."""

_agent = None


def get_research_agent():
    global _agent
    if _agent is None:
        _agent = build_agent("Research_Agent", RESEARCH_TOOLS, SYSTEM_PROMPT)
    return _agent


def handle_research_request(user_message: str, context: str = "") -> str:
    return run_agent(get_research_agent(), user_message, context)


# ---------------------------------------------------------------------------
# Module 8 — Parallel Processing
# ---------------------------------------------------------------------------
def research_single_topic(topic: str) -> ResearchFinding:
    summary = handle_research_request(f"Research the latest news and information about: {topic}")
    return ResearchFinding(source="web_search+wikipedia", query=topic, summary=summary)


def research_multiple_topics_parallel(topics: List[str]) -> List[ResearchFinding]:
    """Run independent research tasks concurrently, e.g.
    'Research Google, Microsoft, Amazon, and OpenAI.'"""
    findings: List[ResearchFinding] = []
    with ThreadPoolExecutor(max_workers=min(4, len(topics)) or 1) as executor:
        future_to_topic = {executor.submit(research_single_topic, t): t for t in topics}
        for future in as_completed(future_to_topic):
            findings.append(future.result())
    # Preserve original topic order in the output
    order = {t: i for i, t in enumerate(topics)}
    findings.sort(key=lambda f: order.get(f.query, 0))
    return findings


def combine_research_findings(findings: List[ResearchFinding]) -> str:
    """Combine parallel research results into one comparative report."""
    llm = get_llm(temperature=0.3)
    joined = "\n\n".join(f"### {f.query}\n{f.summary}" for f in findings)
    prompt = (
        "Combine the following independent research findings into a single, "
        "well-organized comparison report with a short intro, one section per "
        "topic, and a brief closing comparison:\n\n" + joined
    )
    response = llm.invoke(prompt)
    return response.content
