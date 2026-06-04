.PHONY: test lint typecheck fmt check install clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
RUFF = $(VENV)/bin/ruff
MYPY = $(VENV)/bin/mypy

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)/bin/activate
	$(PIP) install pytest pytest-asyncio pytest-mock pytest-cov mcp ruff mypy
	$(PYTHON) install_plugin.py

test: install
	PYTHONPATH=. $(PYTEST) --cov=. --cov-report=term-missing tests/

lint: install
	$(RUFF) check .

typecheck: install
	$(MYPY) .

fmt: install
	$(RUFF) format .

check: fmt lint typecheck test

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
