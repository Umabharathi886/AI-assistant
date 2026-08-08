"""
Module 3 — Research Agent tools: internet search + Wikipedia.
"""
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper

_ddg = DuckDuckGoSearchRun()
_wiki = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=2000)


@tool("web_search", return_direct=False)
def web_search(query: str) -> str:
    """Search the public internet for current information on a topic,
    company, product, or news event. Use this for anything that requires
    up-to-date, real-world information not found in company documents."""
    try:
        return _ddg.run(query)
    except Exception as e:
        return f"Web search failed: {e}"


@tool("wikipedia_search", return_direct=False)
def wikipedia_search(query: str) -> str:
    """Look up background / encyclopedic information on a topic, company,
    or concept using Wikipedia. Good for definitions and general context."""
    try:
        return _wiki.run(query)
    except Exception as e:
        return f"Wikipedia search failed: {e}"


RESEARCH_TOOLS = [web_search]
