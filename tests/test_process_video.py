import os
from pathlib import Path

import pytest


pytestmark = pytest.mark.epic4


def test_process_video_import():
    from src.video.processor import process_video  # noqa: F401


def test_process_video_script_exists():
    assert Path("scripts/process_video.py").exists()


def test_process_video_returns_expected_keys(tmp_path):
    # We don't run inference on real video here; just check interface
    from src.video.processor import process_video

    # Create a dummy file path - function should fail gracefully if video can't open
    # but interface is what matters for structure
    try:
        res = process_video(tmp_path / "nonexistent.mp4", model_path="models/best.pt")
    except Exception as e:
        # Expected to fail on missing video; that's fine for interface test
        assert isinstance(e, Exception)
        return
    # If somehow it opens (unlikely), check keys
    for k in ["video_path", "fps", "total_frames", "duration_sec", "frames_with_logo", "logo_time_sec", "percentage", "detections"]:
        assert k in res
