# db.py
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "caller_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS callers (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            ref_id TEXT PRIMARY KEY,
            caller_id TEXT,
            caller_name TEXT,
            reason TEXT,
            situation_summary TEXT,
            what_agent_checked TEXT,
            urgency TEXT,
            caller_language TEXT,
            preferred_followup TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_caller(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM callers WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row["user_id"],
            "name": row["name"],
            "language_preference": row["language_preference"],
            "facts": json.loads(row["facts"]) if row["facts"] else {},
            "last_interaction": row["last_interaction"]
        }
    return None

def save_caller(user_id: str, name: str, language_preference: str, facts: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    facts_str = json.dumps(facts)
    last_interaction = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO callers (user_id, name, language_preference, facts, last_interaction)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            language_preference = excluded.language_preference,
            facts = excluded.facts,
            last_interaction = excluded.last_interaction
    """, (user_id, name, language_preference, facts_str, last_interaction))
    conn.commit()
    conn.close()

# Initialize DB on load
init_db()


# ---------------------------------------------------------------------------
# Escalation helpers
# ---------------------------------------------------------------------------

SENSITIVE_KEYWORDS = ["otp", "pin", "cvv", "password", "account number", "card number", "aadhaar", "pan"]

def _sanitize_text(text: str) -> str:
    """Return text with any line containing sensitive keywords redacted."""
    clean_lines = []
    for line in text.splitlines():
        lower = line.lower()
        if any(kw in lower for kw in SENSITIVE_KEYWORDS):
            clean_lines.append("[REDACTED – sensitive information removed]")
        else:
            clean_lines.append(line)
    return "\n".join(clean_lines)


def save_escalation(
    ref_id: str,
    caller_id: str,
    caller_name: str,
    reason: str,
    situation_summary: str,
    what_agent_checked: str,
    urgency: str,
    caller_language: str,
    preferred_followup: str,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO escalations
            (ref_id, caller_id, caller_name, reason, situation_summary,
             what_agent_checked, urgency, caller_language, preferred_followup,
             status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
    """, (
        ref_id,
        caller_id,
        _sanitize_text(caller_name),
        reason,
        _sanitize_text(situation_summary),
        _sanitize_text(what_agent_checked),
        urgency,
        caller_language,
        preferred_followup,
        datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()


def get_all_escalations() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM escalations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_escalation_status(ref_id: str, status: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE escalations SET status = ? WHERE ref_id = ?",
        (status, ref_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated
