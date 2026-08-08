"""
Tools shared by the HR Agent (Module 2) and Document Agent (Module 5),
both backed by the ChromaDB retriever (Module 10).
"""
from langchain_core.tools import tool
from knowledge_base.retriever import retrieve_as_context


@tool("search_company_documents", return_direct=False)
def search_company_documents(query: str) -> str:
    """Search the company's uploaded knowledge base (HR policies, employee
    handbook, company guidelines, project docs, SOPs) for information
    relevant to the query. Always use this before answering policy or
    document-related questions."""
    return retrieve_as_context(query)


DOCUMENT_TOOLS = [search_company_documents]
