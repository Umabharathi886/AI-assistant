"""
Enterprise Operations AI Assistant — Streamlit UI.

Ties together the Coordinator Agent, specialist agents (HR, Research,
Email, Document), sequential & parallel workflows, ChromaDB knowledge
base, and SQLite short/long-term memory into one chat application.
"""
import uuid
import streamlit as st

from config import DEPARTMENTS, GDRIVE_ENABLED
from knowledge_base.pdf_loader import load_and_split
from knowledge_base.chroma_setup import add_documents, list_sources, reset_knowledge_base
from memory.sqlite_memory import SQLiteMemory
from memory import short_term, long_term
from workflows.routing import process_employee_request
from workflows.sequential import run_sequential_workflow
from workflows.parallel import run_parallel_research
from utils.file_handler import save_uploaded_file, report_to_txt_bytes, report_to_pdf_bytes

st.set_page_config(page_title="Enterprise Operations AI Assistant", page_icon="🏢", layout="wide")

_memory = SQLiteMemory()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []  # list of dicts: role, content, meta

session_id = st.session_state.session_id

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏢 NovaTech Solutions")
    st.caption("Enterprise Operations AI Assistant")
    st.divider()

    st.markdown("### 📁 Upload Company Documents")
    uploaded_files = st.file_uploader(
        "HR Policies, Employee Handbook, Guidelines, Project Docs, SOPs",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )

    if st.button("🛠️ Build Knowledge Base", use_container_width=True, disabled=not uploaded_files):
        with st.spinner("Indexing documents into ChromaDB..."):
            total_chunks = 0
            for f in uploaded_files:
                path = save_uploaded_file(f)
                chunks = load_and_split(path)
                total_chunks += add_documents(chunks)
            st.success(f"Indexed {total_chunks} chunks from {len(uploaded_files)} file(s).")

    st.markdown("### 📚 View Uploaded Documents")
    sources = list_sources()
    if sources:
        for s in sources:
            st.markdown(f"- {s}")
    else:
        st.caption("No documents indexed yet. Try the sample_documents/ folder.")

    if st.button("🗑️ Reset Knowledge Base", use_container_width=True):
        reset_knowledge_base()
        st.success("Knowledge base cleared.")
        st.rerun()

    st.divider()
    st.markdown("### 🕘 Previous Conversations")
    past_sessions = [s for s in _memory.list_sessions() if s != session_id]
    if past_sessions:
        chosen = st.selectbox("Load a past session", ["(none)"] + past_sessions)
        if chosen != "(none)" and st.button("Load", use_container_width=True):
            st.session_state.session_id = chosen
            st.session_state.chat_log = [
                {"role": m["role"], "content": m["content"], "meta": {"agent": m.get("agent")}}
                for m in _memory.get_conversation(chosen)
            ]
            st.rerun()
    else:
        st.caption("No previous sessions yet.")

    if st.button("🧹 Clear Chat", use_container_width=True):
        _memory.clear_session(session_id)
        short_term.clear_session(session_id)
        st.session_state.chat_log = []
        st.rerun()

    st.divider()
    with st.expander("⚙️ Advanced: Multi-topic Parallel Research"):
        topics_raw = st.text_area("Comma-separated topics", placeholder="Google, Microsoft, Amazon, OpenAI")
        if st.button("Run Parallel Research", use_container_width=True, disabled=not topics_raw):
            topics = [t.strip() for t in topics_raw.split(",") if t.strip()]
            with st.spinner(f"Researching {len(topics)} topics in parallel..."):
                result = run_parallel_research(topics)
            st.session_state.chat_log.append({
                "role": "assistant",
                "content": result["combined_report"],
                "meta": {"agent": "RESEARCH (parallel)", "findings": result["findings"]},
            })
            st.rerun()

    with st.expander("⚙️ Advanced: Sequential Workflow"):
        st.caption("Research → Summarize → Draft Email → Send → Store")
        seq_topic = st.text_input("Topic to research")
        seq_recipient = st.text_input("Email recipient (optional)")
        if st.button("Run Sequential Workflow", use_container_width=True, disabled=not seq_topic):
            with st.spinner("Running sequential pipeline..."):
                result = run_sequential_workflow(seq_topic, seq_recipient, session_id)
            st.session_state.chat_log.append({
                "role": "assistant",
                "content": result["email_draft"],
                "meta": {"agent": "SEQUENTIAL_WORKFLOW", "status": result["send_status"]},
            })
            st.rerun()

    if GDRIVE_ENABLED:
        st.divider()
        st.markdown("### ☁️ Google Drive (Module 14)")
        st.caption("Upload reports, search previous reports, store generated documents.")
    st.divider()
    st.caption(f"Session ID: `{session_id}`")
    st.caption(f"Departments: {', '.join(DEPARTMENTS)}")

# ---------------------------------------------------------------------------
# Main screen — Professional Chat Interface
# ---------------------------------------------------------------------------
st.title("Enterprise Operations AI Assistant")
st.caption("Ask about HR policies, request research, draft/send emails, or search company documents.")

for entry in st.session_state.chat_log:
    with st.chat_message(entry["role"]):
        meta = entry.get("meta", {})
        if meta.get("agent"):
            st.markdown(f"**Agent:** `{meta['agent']}`")
        st.markdown(entry["content"])

        if "report" in meta:
            report = meta["report"]
            with st.expander("📋 Generated Report (Structured Output)"):
                st.markdown(report.to_markdown())
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("⬇️ Download TXT", report_to_txt_bytes(report),
                                        file_name="report.txt", mime="text/plain",
                                        key=f"txt_{id(entry)}")
                with col2:
                    st.download_button("⬇️ Download PDF", report_to_pdf_bytes(report),
                                        file_name="report.pdf", mime="application/pdf",
                                        key=f"pdf_{id(entry)}")

        if meta.get("sub_tasks"):
            with st.expander("🔧 Tool Execution Summary"):
                st.markdown("**Reasoning:** " + meta.get("reasoning", ""))
                st.markdown("**Sub-tasks identified:**")
                for t in meta["sub_tasks"]:
                    st.markdown(f"- {t}")

        if meta.get("findings"):
            with st.expander("📄 Retrieved / Research Sources"):
                for f in meta["findings"]:
                    st.markdown(f"**{f['query']}**\n\n{f['summary']}")
                    st.divider()

user_input = st.chat_input("e.g. What is our work from home policy?")

if user_input:
    st.session_state.chat_log.append({"role": "user", "content": user_input, "meta": {}})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Routing to the right agent..."):
            result = process_employee_request(user_input, session_id)

        st.markdown(f"**Agent:** `{result['agent']}`")
        st.markdown(result["response"])

        with st.expander("🔧 Tool Execution Summary"):
            st.markdown("**Routing reasoning:** " + result["reasoning"])
            if result["sub_tasks"]:
                st.markdown("**Sub-tasks identified:**")
                for t in result["sub_tasks"]:
                    st.markdown(f"- {t}")
            else:
                st.caption("Single-agent request — no sub-tasks.")

        report = result["report"]
        with st.expander("📋 Generated Report (Structured Output)"):
            st.markdown(report.to_markdown())
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("⬇️ Download TXT", report_to_txt_bytes(report),
                                    file_name="report.txt", mime="text/plain", key="txt_latest")
            with col2:
                st.download_button("⬇️ Download PDF", report_to_pdf_bytes(report),
                                    file_name="report.pdf", mime="application/pdf", key="pdf_latest")

    st.session_state.chat_log.append({
        "role": "assistant",
        "content": result["response"],
        "meta": {
            "agent": result["agent"],
            "reasoning": result["reasoning"],
            "sub_tasks": result["sub_tasks"],
            "report": report,
        },
    })
