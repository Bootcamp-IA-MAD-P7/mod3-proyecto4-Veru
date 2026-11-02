from pathlib import Path

import pytest


pytestmark = pytest.mark.epic6


def test_docker_files_exist():
    assert Path("Dockerfile").exists()
    assert Path("docker-compose.yml").exists()
