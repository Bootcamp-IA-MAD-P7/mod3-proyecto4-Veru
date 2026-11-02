from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


DEFAULT_DB = Path("data/db/logotracker.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = get_connection(db_path)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    return conn
