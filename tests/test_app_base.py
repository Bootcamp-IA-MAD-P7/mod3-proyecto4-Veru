import importlib

import pytest


pytestmark = pytest.mark.epic5


def test_app_modules_import():
    import app  # noqa: F401
    import app.main  # noqa: F401
    import app.Home  # noqa: F401
