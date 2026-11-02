from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .database import DEFAULT_DB, init_db


def save_video_result(
    result: Dict[str, Any],
    db_path: str | Path = DEFAULT_DB,
) -> int:
    conn = init_db(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO videos (filename, filepath, fps, total_frames, duration_sec, frames_with_logo, logo_time_sec, percentage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            Path(result["video_path"]).name,
            str(result["video_path"]),
            result.get("fps"),
            result.get("total_frames"),
            result.get("duration_sec"),
            result.get("frames_with_logo"),
            result.get("logo_time_sec"),
            result.get("percentage"),
        ),
    )
    video_id = cur.lastrowid
    detections = result.get("detections") or []
    for det in detections:
        bbox = det.get("bbox") or [None, None, None, None]
        cur.execute(
            """
            INSERT INTO detections (video_id, frame_idx, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, crop_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                det.get("frame_idx"),
                det.get("class_name"),
                det.get("confidence"),
                bbox[0] if len(bbox) > 0 else None,
                bbox[1] if len(bbox) > 1 else None,
                bbox[2] if len(bbox) > 2 else None,
                bbox[3] if len(bbox) > 3 else None,
                det.get("crop_path"),
            ),
        )
    conn.commit()
    conn.close()
    return int(video_id)


def get_videos(db_path: str | Path = DEFAULT_DB) -> List[sqlite3.Row]:
    conn = init_db(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM videos ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows
