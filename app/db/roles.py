# app/db/roles.py
import sqlite3
from pathlib import Path

DB_PATH = Path("jobfit.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            title TEXT,
            context TEXT,
            min_years_exp INTEGER,
            required_tech TEXT,
            requires_degree TEXT,
            must_haves TEXT,
            nice_to_have TEXT,
            red_flags TEXT,
            num_questions INTEGER
        );
        """
    )
    conn.commit()
    conn.close()

def add_role(role_profile: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO roles (
            company_name, title, context,
            min_years_exp, required_tech, requires_degree,
            must_haves, nice_to_have, red_flags, num_questions
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            role_profile.get("company_name"),
            role_profile.get("title"),
            role_profile.get("context"),
            role_profile.get("min_years_exp"),
            role_profile.get("required_tech"),
            role_profile.get("requires_degree"),
            role_profile.get("must_haves"),
            role_profile.get("nice_to_have"),
            role_profile.get("red_flags"),
            role_profile.get("num_questions"),
        ),
    )
    role_id = cur.lastrowid
    conn.commit()
    conn.close()
    return role_id


def list_roles():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, company_name, title FROM roles ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_role(role_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id, company_name, title, context,
            min_years_exp, required_tech, requires_degree,
            must_haves, nice_to_have, red_flags, num_questions
        FROM roles
        WHERE id = ?
        """,
        (role_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    (
        _id, company_name, title, context,
        min_years_exp, required_tech, requires_degree,
        must_haves, nice_to_have, red_flags, num_questions
    ) = row
    return {
        "id": _id,
        "company_name": company_name,
        "title": title,
        "context": context,
        "min_years_exp": min_years_exp,
        "required_tech": required_tech,
        "requires_degree": requires_degree,
        "must_haves": must_haves,
        "nice_to_have": nice_to_have,
        "red_flags": red_flags,
        "num_questions": num_questions,
    }

def delete_role(role_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    conn.close()

def update_role(role_id: int, role_profile: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE roles
        SET company_name = ?,
            title = ?,
            context = ?,
            min_years_exp = ?,
            required_tech = ?,
            requires_degree = ?,
            must_haves = ?,
            nice_to_have = ?,
            red_flags = ?,
            num_questions = ?
        WHERE id = ?
        """,
        (
            role_profile.get("company_name"),
            role_profile.get("title"),
            role_profile.get("context"),
            role_profile.get("min_years_exp"),
            role_profile.get("required_tech"),
            role_profile.get("requires_degree"),
            role_profile.get("must_haves"),
            role_profile.get("nice_to_have"),
            role_profile.get("red_flags"),
            role_profile.get("num_questions"),
            role_id,
        ),
    )
    conn.commit()
    conn.close()
