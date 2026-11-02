from pathlib import Path

import pytest


pytestmark = pytest.mark.epic5


def test_report_page_exists():
    assert Path("app/pages/2_Report.py").exists()
