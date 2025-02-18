from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from backend.app.config import get_settings


def _db_path() -> Path:
    url = get_settings().database_url
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", "", 1))
    return Path("data/statvisor.db")


def init_db() -> None:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                route TEXT NOT NULL,
                answer TEXT NOT NULL,
                trace_json TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_query(session_id: str, question: str, route: str, answer: str, trace: list[str]) -> None:
    path = _db_path()
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO query_audit (created_at, session_id, question, route, answer, trace_json) VALUES (?, ?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                session_id,
                question,
                route,
                answer,
                json.dumps(trace),
            ),
        )
        conn.commit()


def recent_queries(limit: int = 20) -> list[dict]:
    path = _db_path()
    if not path.exists():
        return []
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, created_at, session_id, question, route, answer, trace_json FROM query_audit ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["trace"] = json.loads(item.pop("trace_json"))
        out.append(item)
    return out
