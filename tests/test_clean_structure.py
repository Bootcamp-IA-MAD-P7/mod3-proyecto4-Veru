from pathlib import Path

import pytest


pytestmark = pytest.mark.epic6


def test_required_dirs():
    for p in ["src/video", "src/db", "app", "scripts", "tests", "data/crops", "data/uploads", "data/db"]:
        assert Path(p).exists()
