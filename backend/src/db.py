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
