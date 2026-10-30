PYTHON ?= python
PYTEST = $(PYTHON) -m pytest

.PHONY: help install test test-unit test-smoke test-epic2 test-epic3 test-epic4 test-epic5 test-epic6 compile check clean

help:
	@echo "LogoExposure-Tracker"
	@echo ""
	@echo "  make install      Install runtime and dev dependencies"
	@echo "  make test         Run the full pytest suite"
	@echo "  make test-unit    Run tests that are not marked as smoke"
	@echo "  make test-smoke   Run fast integration smoke tests"
	@echo "  make test-epic2   Run dataset/labeling tests"
	@echo "  make test-epicN   Run tests for an epic (N = 2..6)"
	@echo "  make compile      Byte-compile scripts, src and app"
	@echo "  make check        Compile + full test suite (run before closing an issue)"
	@echo "  make clean        Remove Python and pytest caches"

install:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

test:
	$(PYTEST)

test-unit:
	$(PYTEST) -m "not smoke"

test-smoke:
	$(PYTEST) -m smoke

test-epic2:
	$(PYTEST) -m epic2

test-epic3:
	$(PYTEST) -m epic3

test-epic4:
	$(PYTEST) -m epic4

test-epic5:
	$(PYTEST) -m epic5

test-epic6:
	$(PYTEST) -m epic6

compile:
	$(PYTHON) -m compileall -q scripts src app

check: compile test

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
