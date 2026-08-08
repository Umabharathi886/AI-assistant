"""
Shared helper for building each specialized agent with LangChain's
create_agent() (falls back to LangGraph's create_react_agent on older
LangChain versions where create_agent isn't yet available).

LLM provider is switchable via config.LLM_PROVIDER:
- "groq"   (default): free tier, no credit card, e.g. llama-3.3-70b-versatile
- "openai": paid, e.g. gpt-4o-mini
"""
from config import (
    LLM_PROVIDER,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

try:
    from langchain.agents import create_agent as _create_agent
    _USING_NATIVE = True
except ImportError:  # pragma: no cover - version fallback
    from langgraph.prebuilt import create_react_agent as _create_agent
    _USING_NATIVE = False


def get_llm(temperature: float = 0.2):
    """Return a chat model based on LLM_PROVIDER. Both ChatGroq and
    ChatOpenAI implement the same .invoke() / tool-calling interface, so
    the rest of the app doesn't need to know which one is active."""
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        if not OPENAI_API_KEY:
            raise ValueError("LLM_PROVIDER is 'openai' but OPENAI_API_KEY is not set in .env")
        return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=temperature)

    # default: groq (free)
    from langchain_groq import ChatGroq
    if not GROQ_API_KEY:
        raise ValueError(
            "LLM_PROVIDER is 'groq' but GROQ_API_KEY is not set in .env. "
            "Get a free key at https://console.groq.com"
        )
    return ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=temperature)


def build_agent(name: str, tools: list, system_prompt: str, temperature: float = 0.2):
    """Build a tool-using agent executor. Returns an object exposing
    .invoke({"messages": [...]}) per the LangGraph/create_agent interface."""
    llm = get_llm(temperature=temperature)
    if _USING_NATIVE:
        return _create_agent(model=llm, tools=tools, system_prompt=system_prompt, name=name)
    return _create_agent(model=llm, tools=tools, prompt=system_prompt)


def run_agent(agent, user_message: str, context: str = "") -> str:
    """Invoke an agent built by build_agent() and return the final text reply."""
    full_input = f"{context}\n\nEmployee request: {user_message}" if context else user_message
    result = agent.invoke({"messages": [{"role": "user", "content": full_input}]})
    messages = result["messages"]
    # Last AI message holds the final answer
    for msg in reversed(messages):
        role = getattr(msg, "type", None) or getattr(msg, "role", None)
        if role in ("ai", "assistant"):
            return msg.content
    return messages[-1].content if messages else ""
