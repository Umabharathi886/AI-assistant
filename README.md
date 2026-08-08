# Enterprise Operations AI Assistant

A multi-agent business automation platform built with **LangChain** and
deployed with **Streamlit**. A Coordinator Agent routes employee
requests to specialized HR, Research, Email, and Document agents, backed
by a ChromaDB knowledge base and SQLite short/long-term memory.

## Architecture

```
Employee → Streamlit UI → Enterprise AI Coordinator
                              ├── HR Agent        (ChromaDB RAG)
                              ├── Research Agent   (Web search + Wikipedia)
                              ├── Email Agent      (Gmail toolkit / draft)
                              └── Document Agent   (ChromaDB RAG)
                              ↓
                    Shared Memory Layer (SQLite + long-term facts)
                              ↓
                    Company Knowledge Base (ChromaDB)
```

## Project Structure

```
AI-assistant/
├── app.py                     # Streamlit application (entry point)
├── config.py                  # Central configuration
├── requirements.txt
├── .env.example                # Copy to .env and fill in your keys
├── agents/
│   ├── base.py                 # create_agent() factory shared by all agents
│   ├── coordinator.py          # Module 6/9 — routing + RunnableBranch
│   ├── hr_agent.py              # Module 2
│   ├── research_agent.py        # Module 3 + parallel research helpers
│   ├── email_agent.py           # Module 4
│   └── document_agent.py        # Module 5
├── tools/
│   ├── search_tool.py           # web_search, wikipedia_search
│   ├── gmail_tool.py             # draft/read/send email
│   ├── document_tool.py          # ChromaDB-backed document search
│   └── python_tool.py            # Module 13 — calculations, CSV, tables
├── knowledge_base/
│   ├── pdf_loader.py              # Module 10 — loader + splitter
│   ├── chroma_setup.py            # Module 10 — ChromaDB collection
│   └── retriever.py               # Shared retriever for HR/Document agents
├── memory/
│   ├── short_term.py              # In-RAM current-session memory
│   ├── sqlite_memory.py            # Module 11 — persistent conversations
│   └── long_term.py                # Module 11 — employee profile facts
├── workflows/
│   ├── sequential.py                # Module 7 — Research→Summarize→Email→Send→Store
│   ├── parallel.py                  # Module 8 — RunnableParallel / threaded research
│   └── routing.py                   # Orchestrates coordinator + memory + reports
├── models/
│   └── schemas.py                    # Module 12 — Pydantic structured outputs
├── utils/
│   ├── report_generator.py            # Structured report generation (LLM + Pydantic)
│   └── file_handler.py                 # TXT/PDF export, upload persistence
├── sample_documents/                   # Sample HR policies, SOP, handbook, CSV
└── data/                                # SQLite DB + ChromaDB persistence (gitignored)
```

## Setup

1. **Clone/copy this folder**, then create a virtual environment:
   ```bash
   cd AI-assistant
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   The first run will also download a small local embedding model
   (~90MB, `sentence-transformers/all-MiniLM-L6-v2`) automatically — no
   API key needed for that.

   If you plan to use the live Gmail toolkit (optional), also install:
   ```bash
   pip install langchain-google-community google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

3. **Configure environment variables:**
   ```bash
   copy .env.example .env         # Windows
   # cp .env.example .env         # macOS/Linux
   ```
   Open `.env` and set `GROQ_API_KEY` (required, free). Everything else
   has sensible defaults.

   **Get a free Groq API key:**
   1. Go to https://console.groq.com and sign in (Google/GitHub, no
      credit card needed).
   2. Click **API Keys** → **Create API Key**.
   3. Copy the key into `.env` as `GROQ_API_KEY=...`.

   By default the app runs entirely free:
   - **LLM:** Groq (`llama-3.3-70b-versatile`) — `LLM_PROVIDER=groq`
   - **Embeddings:** local `sentence-transformers` model — `EMBEDDING_PROVIDER=huggingface`

   To switch to OpenAI instead (paid), set `LLM_PROVIDER=openai` and/or
   `EMBEDDING_PROVIDER=openai` in `.env` and fill in `OPENAI_API_KEY`.

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   The app opens at `http://localhost:8501`.

5. **Build the knowledge base:** In the sidebar, upload files from
   `sample_documents/` (or your own PDFs/TXT files) and click
   **"Build Knowledge Base."**

## Gmail Setup (Module 4, optional)

By default the Email Agent runs in **draft-only mode** — it writes email
text but does not send anything, so the app works out of the box.

To enable live Gmail read/send:
1. In [Google Cloud Console](https://console.cloud.google.com/), create a
   project and enable the **Gmail API**.
2. Create an **OAuth Client ID** (Application type: Desktop app).
3. Download the JSON and save it to `data/gmail_credentials.json`.
4. In `.env`, set `GMAIL_ENABLED=true`.
5. Install the Gmail extras (see step 2 above).
6. On first use, a browser window opens for you to authorize access; a
   token is cached to `data/gmail_token.json` for future runs.

## Google Drive Setup (Module 14, optional)

Set `GDRIVE_ENABLED=true` in `.env` and place OAuth credentials at
`data/gdrive_credentials.json` (same Google Cloud project, with the
Drive API enabled and a Desktop OAuth client). The sidebar will then
surface Drive upload/search controls.

## Example Requests to Try

- "What is our work from home policy?"
- "Summarize the employee handbook and email it to HR."
- "Research Microsoft's latest AI products."
- "Research Google, Microsoft, Amazon, and OpenAI." (sidebar → Parallel Research)
- "Remember that I belong to the Finance Department."
- "What department do I belong to?"
- "Calculate employee attendance percentage from sample_attendance.csv."
- "Draft an email requesting three days leave."

## Notes

- **LLM provider:** Uses **Groq** via `langchain-groq` by default
  (`llama-3.3-70b-versatile`), which is free with no credit card
  required. Switch to OpenAI or another provider by editing
  `LLM_PROVIDER` in `.env` and `agents/base.py`'s `get_llm()` — the
  rest of the app is provider-agnostic since it only depends on the
  standard LangChain chat model `.invoke()` interface.
- **Embeddings:** Uses a local `sentence-transformers` model by
  default (`EMBEDDING_PROVIDER=huggingface`) — runs on your machine,
  no API key or cost. Switch to OpenAI embeddings via
  `EMBEDDING_PROVIDER=openai` in `.env` if preferred.
- **Vector store:** ChromaDB persists to `data/chroma_db/` so the
  knowledge base survives app restarts.
- **Memory:** Conversations persist to `data/memory.db` (SQLite); use
  the sidebar "Previous Conversations" panel to reload any session.
- **Rate limits:** Groq's free tier has generous but finite
  requests/tokens-per-minute limits. If you hit a rate-limit error
  during heavy testing (e.g. parallel research across many topics),
  wait a minute and retry, or reduce concurrent topics.
