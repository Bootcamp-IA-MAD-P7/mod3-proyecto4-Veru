from pathlib import Path

import pytest


pytestmark = pytest.mark.epic6


def test_readme_has_docker():
    text = Path("README.md").read_text(encoding="utf-8", errors="ignore")
    assert "docker" in text.lower()
