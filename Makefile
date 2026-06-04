.PHONY: test lint fmt checks install

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
RUFF = $(VENV)/bin/ruff

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)/bin/activate
	$(PIP) install pytest pytest-asyncio pytest-mock mcp ruff
	$(PYTHON) install_plugin.py

test: install
	PYTHONPATH=. $(PYTEST) tests/

lint: install
	$(RUFF) check .

fmt: install
	$(RUFF) format .

check: fmt lint test
