import pytest

from src.db import database, repository


pytestmark = pytest.mark.epic4


def test_save_video_result(tmp_path):
    db = tmp_path / "test.db"
    result = {
        "video_path": "data/uploads/test.mp4",
        "fps": 30.0,
        "total_frames": 300,
        "duration_sec": 10.0,
        "frames_with_logo": 30,
        "logo_time_sec": 1.0,
        "percentage": 10.0,
        "detections": [
            {
                "frame_idx": 10,
                "class_name": "proton_logo",
                "confidence": 0.9,
                "bbox": [1, 2, 3, 4],
                "crop_path": "data/crops/test.jpg",
            }
        ],
    }
    vid_id = repository.save_video_result(result, db_path=db)
    assert vid_id > 0
    conn = database.get_connection(db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM videos")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT COUNT(*) FROM detections")
    assert cur.fetchone()[0] == 1
    conn.close()
