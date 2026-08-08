"""
Download Options support: export a structured report as TXT or PDF, and
persist Streamlit-uploaded files to disk so the knowledge base loaders
can read them.
"""
import io
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from models.schemas import AgentReport
from config import DATA_DIR

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file) -> str:
    """Persist a Streamlit UploadedFile to disk and return its path."""
    dest = UPLOAD_DIR / uploaded_file.name
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)


def report_to_txt_bytes(report: AgentReport) -> bytes:
    return report.to_markdown().encode("utf-8")


def report_to_pdf_bytes(report: AgentReport) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER,
                             leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                             topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6)
    body = styles["BodyText"]

    story = [Paragraph("Enterprise Operations AI Assistant — Report", styles["Title"]), Spacer(1, 12)]

    def add_section(title: str, content: str):
        story.append(Paragraph(title, heading))
        story.append(Paragraph(content.replace("\n", "<br/>"), body))

    add_section("Task Summary", report.task_summary)
    add_section("Department", report.department.value)
    add_section("Priority", report.priority.value)
    add_section("Actions Taken", "<br/>".join(f"- {a}" for a in report.actions_taken) or "None")
    add_section("Pending Actions", "<br/>".join(f"- {a}" for a in report.pending_actions) or "None")
    add_section("Recommended Next Steps", "<br/>".join(f"- {a}" for a in report.recommended_next_steps) or "None")

    doc.build(story)
    return buffer.getvalue()
