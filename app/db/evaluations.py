# app/db/evaluations.py
import sqlite3, json
from pathlib import Path

DB_PATH = Path("jobfit.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_evaluations_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER,
            candidate_name TEXT,
            candidate_email TEXT,
            candidate_phone TEXT,
            answers_json TEXT,
            scores_json TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()

def save_evaluation(role_id: int, candidate: dict, answers: dict,
                    scores: dict, summary: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO evaluations (
            role_id, candidate_name, candidate_email, candidate_phone,
            answers_json, scores_json, summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            role_id,
            candidate.get("name"),
            candidate.get("email"),
            candidate.get("phone"),
            json.dumps(answers),
            json.dumps(scores),
            summary,
        ),
    )
    conn.commit()
    conn.close()

def list_evaluations():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at, role_id, candidate_name, candidate_email, candidate_phone
        FROM evaluations
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_evaluation(eval_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, role_id, candidate_name, candidate_email, candidate_phone,
               answers_json, scores_json, summary, created_at
        FROM evaluations
        WHERE id = ?
        """,
        (eval_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None

    (
        _id, role_id, name, email, phone,
        answers_json, scores_json, summary, created_at
    ) = row

    return {
        "id": _id,
        "role_id": role_id,
        "candidate_name": name,
        "candidate_email": email,
        "candidate_phone": phone,
        "answers_json": answers_json,
        "scores_json": scores_json,
        "summary": summary,
        "created_at": created_at,
    }
