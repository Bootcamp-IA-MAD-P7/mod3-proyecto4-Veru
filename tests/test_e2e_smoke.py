import pytest


pytestmark = [pytest.mark.epic6, pytest.mark.smoke]


def test_e2e_components_exist():
    from pathlib import Path
    assert Path("app/Home.py").exists()
    assert Path("scripts/process_video.py").exists()
    assert Path("models/best.pt").exists() or Path("models/yolov8n.pt").exists()
    assert Path("src/db/schema.sql").exists()
