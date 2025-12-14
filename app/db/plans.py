# app/db/plans.py
import sqlite3, json
from pathlib import Path

DB_PATH = Path("jobfit.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_plans_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS role_plans (
            role_id INTEGER PRIMARY KEY,
            plan_json TEXT
        );
        """
    )
    conn.commit()
    conn.close()

def get_plan_for_role(role_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT plan_json FROM role_plans WHERE role_id = ?", (role_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row[0])

def save_plan_for_role(role_id: int, plan: list):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO role_plans (role_id, plan_json)
        VALUES (?, ?)
        ON CONFLICT(role_id) DO UPDATE SET plan_json = excluded.plan_json
        """,
        (role_id, json.dumps(plan)),
    )
    conn.commit()
    conn.close()
