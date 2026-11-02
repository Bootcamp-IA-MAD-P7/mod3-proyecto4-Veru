import os
from pathlib import Path

import numpy as np
import pytest

from src.video import crops


pytestmark = pytest.mark.epic4


def test_ensure_crops_dir(tmp_path):
    d = crops.ensure_crops_dir(tmp_path / "crops")
    assert d.exists()
    assert d.is_dir()


def test_save_crop(tmp_path):
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    bbox = [10, 10, 50, 50]
    path = crops.save_crop(frame, bbox, tmp_path, "video", 1, 0)
    assert path is not None
    assert path.exists()
    assert path.suffix == ".jpg"


def test_save_crop_invalid_bbox(tmp_path):
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    bbox = [50, 50, 10, 10]
    path = crops.save_crop(frame, bbox, tmp_path, "video", 1, 0)
    assert path is None
