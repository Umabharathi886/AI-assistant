"""
Module 11 — Persistent Memory (SQLite).

Two responsibilities:
1. Store every conversation turn so it can be reloaded ("Previous Conversations").
2. Store long-term employee facts (name, department, preferences, frequent
   questions / documents) that persist across sessions.
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

from config import SQLITE_DB_PATH
from models.schemas import EmployeeProfile


SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    agent TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employee_profile (
    session_id TEXT PRIMARY KEY,
    employee_name TEXT,
    department TEXT,
    preferred_email_style TEXT,
    frequently_asked_questions TEXT DEFAULT '[]',
    frequently_accessed_documents TEXT DEFAULT '[]',
    updated_at TEXT
);
"""


class SQLiteMemory:
    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    # ------------------------------------------------------------------
    # Conversation (short-term persisted) memory
    # ------------------------------------------------------------------
    def add_message(self, session_id: str, role: str, content: str, agent: Optional[str] = None):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (session_id, role, content, agent, created_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, agent, datetime.utcnow().isoformat()),
            )

    def get_conversation(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT role, content, agent, created_at FROM conversations "
                "WHERE session_id = ? ORDER BY id ASC LIMIT ?",
                (session_id, limit),
            )
            rows = cur.fetchall()
        return [
            {"role": r[0], "content": r[1], "agent": r[2], "created_at": r[3]}
            for r in rows
        ]

    def list_sessions(self) -> List[str]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT DISTINCT session_id FROM conversations ORDER BY session_id DESC"
            )
            return [r[0] for r in cur.fetchall()]

    def clear_session(self, session_id: str):
        with self._connect() as conn:
            conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))

    # ------------------------------------------------------------------
    # Long-term employee profile memory
    # ------------------------------------------------------------------
    def get_profile(self, session_id: str) -> EmployeeProfile:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT employee_name, department, preferred_email_style, "
                "frequently_asked_questions, frequently_accessed_documents "
                "FROM employee_profile WHERE session_id = ?",
                (session_id,),
            )
            row = cur.fetchone()
        if not row:
            return EmployeeProfile()
        return EmployeeProfile(
            employee_name=row[0],
            department=row[1],
            preferred_email_style=row[2],
            frequently_asked_questions=json.loads(row[3] or "[]"),
            frequently_accessed_documents=json.loads(row[4] or "[]"),
        )

    def update_profile(self, session_id: str, **fields):
        profile = self.get_profile(session_id)
        data = profile.model_dump()

        for key, value in fields.items():
            if key not in data:
                continue
            if key in ("frequently_asked_questions", "frequently_accessed_documents"):
                if value and value not in data[key]:
                    data[key].append(value)
            else:
                data[key] = value

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO employee_profile
                    (session_id, employee_name, department, preferred_email_style,
                     frequently_asked_questions, frequently_accessed_documents, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    employee_name=excluded.employee_name,
                    department=excluded.department,
                    preferred_email_style=excluded.preferred_email_style,
                    frequently_asked_questions=excluded.frequently_asked_questions,
                    frequently_accessed_documents=excluded.frequently_accessed_documents,
                    updated_at=excluded.updated_at
                """,
                (
                    session_id,
                    data["employee_name"],
                    data["department"],
                    data["preferred_email_style"],
                    json.dumps(data["frequently_asked_questions"]),
                    json.dumps(data["frequently_accessed_documents"]),
                    datetime.utcnow().isoformat(),
                ),
            )
