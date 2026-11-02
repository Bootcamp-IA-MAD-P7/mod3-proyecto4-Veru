import sqlite3
from pathlib import Path

import pytest

from src.db import database


pytestmark = pytest.mark.epic4


def test_init_db_creates_tables(tmp_path):
    db = tmp_path / "test.db"
    conn = database.init_db(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert "videos" in tables
    assert "detections" in tables
    conn.close()


def test_detections_has_fk_to_videos(tmp_path):
    db = tmp_path / "test.db"
    conn = database.init_db(db)
    cur = conn.cursor()
    # Try to insert detection without video
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO detections (video_id, frame_idx) VALUES (999, 1)")
        conn.commit()
    conn.close()
