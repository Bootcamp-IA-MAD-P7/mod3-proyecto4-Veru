import pytest

from src.video import metrics


pytestmark = pytest.mark.epic4


def test_compute_duration():
    assert metrics.compute_duration(100, 25.0) == 4.0
    assert metrics.compute_duration(0, 30.0) == 0.0
    assert metrics.compute_duration(10, 0.0) == 0.0


def test_compute_screen_time():
    assert metrics.compute_screen_time(50, 25.0) == 2.0
    assert metrics.compute_screen_time(0, 30.0) == 0.0
    assert metrics.compute_screen_time(10, 0.0) == 0.0


def test_compute_percentage():
    assert metrics.compute_percentage(25, 100) == 25.0
    assert metrics.compute_percentage(0, 100) == 0.0
    assert metrics.compute_percentage(100, 0) == 0.0
    assert metrics.compute_percentage(-1, 100) == 0.0
    assert metrics.compute_percentage(200, 100) == 100.0
