import pytest


pytestmark = pytest.mark.epic5


def test_analyze_page_exists():
    from pathlib import Path
    assert Path("app/pages/1_Analyze.py").exists()
