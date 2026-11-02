from pathlib import Path

import pytest


pytestmark = pytest.mark.epic5


def test_history_page_exists():
    assert Path("app/pages/3_History.py").exists()
