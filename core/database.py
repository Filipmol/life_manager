"""
Database module — SQLite with auto-creation of all tables on first launch.
Thread-safe: every public function opens its own connection so Flet's
async / threaded callbacks never share a handle.
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Optional

DB_DIR = os.path.join(os.path.expanduser("~"), ".life_manager")
DB_PATH = os.path.join(DB_DIR, "life_manager.db")


def _connect() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    """Create every table if it does not exist yet."""
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredients TEXT    NOT NULL,
            recipe_text TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            goal         TEXT    NOT NULL,
            plan_text    TEXT    NOT NULL,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    NOT NULL DEFAULT '',
            category    TEXT    NOT NULL DEFAULT 'work',
            status      TEXT    NOT NULL DEFAULT 'todo',
            priority    INTEGER NOT NULL DEFAULT 0,
            due_date    TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );
    """)

    conn.commit()
    conn.close()


# ─── Recipes ────────────────────────────────────────────────────────

def save_recipe(ingredients: str, recipe_text: str) -> int:
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO recipes (ingredients, recipe_text) VALUES (?, ?)",
        (ingredients, recipe_text),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_recipes(limit: int = 50) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM recipes ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_recipe(recipe_id: int) -> None:
    conn = _connect()
    conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    conn.close()


# ─── Workouts ───────────────────────────────────────────────────────

def save_workout(goal: str, plan_text: str) -> int:
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO workouts (goal, plan_text) VALUES (?, ?)",
        (goal, plan_text),
    )
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def get_workouts(limit: int = 50) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM workouts ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_workout(workout_id: int) -> None:
    conn = _connect()
    conn.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    conn.commit()
    conn.close()


# ─── Tasks ──────────────────────────────────────────────────────────

def add_task(
    title: str,
    description: str = "",
    category: str = "work",
    status: str = "todo",
    priority: int = 0,
    due_date: Optional[str] = None,
) -> int:
    conn = _connect()
    cur = conn.execute(
        """INSERT INTO tasks (title, description, category, status, priority, due_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, category, status, priority, due_date),
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def get_tasks(category: Optional[str] = None) -> list[dict]:
    conn = _connect()
    if category:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE category = ? ORDER BY priority DESC, created_at DESC",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY priority DESC, created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_task(task_id: int, **kwargs) -> None:
    allowed = {"title", "description", "category", "status", "priority", "due_date"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [task_id]
    conn = _connect()
    conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_task(task_id: int) -> None:
    conn = _connect()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


# ─── Dashboard stats ────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    conn = _connect()

    today = date.today().isoformat()

    total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    todo_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'todo'"
    ).fetchone()[0]
    doing_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'doing'"
    ).fetchone()[0]
    done_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'done'"
    ).fetchone()[0]

    recipes_today = conn.execute(
        "SELECT COUNT(*) FROM recipes WHERE date(created_at) = ?", (today,)
    ).fetchone()[0]
    total_recipes = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]

    workouts_today = conn.execute(
        "SELECT COUNT(*) FROM workouts WHERE date(created_at) = ?", (today,)
    ).fetchone()[0]
    total_workouts = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]

    overdue = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status != 'done'",
        (today,),
    ).fetchone()[0]

    conn.close()
    return {
        "total_tasks": total_tasks,
        "todo_tasks": todo_tasks,
        "doing_tasks": doing_tasks,
        "done_tasks": done_tasks,
        "recipes_today": recipes_today,
        "total_recipes": total_recipes,
        "workouts_today": workouts_today,
        "total_workouts": total_workouts,
        "overdue_tasks": overdue,
    }
