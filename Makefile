PYTHON ?= .venv/bin/python
RUFF ?= .venv/bin/ruff
PYTHON_VERSION ?= 3.13.15

RUFF_TARGETS := bot.py infrastructure tgbot scripts tests

.PHONY: setup format lint test check preflight verify-db run

setup:
	UV_LINK_MODE=copy uv venv --python $(PYTHON_VERSION)
	UV_LINK_MODE=copy uv pip install --python $(PYTHON) -r requirements-dev.txt

format:
	$(RUFF) check --fix $(RUFF_TARGETS)
	$(RUFF) format $(RUFF_TARGETS)

lint:
	$(RUFF) check $(RUFF_TARGETS)
	$(RUFF) format --check $(RUFF_TARGETS)

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) -m compileall -q bot.py infrastructure tgbot scripts tests
	$(RUFF) check $(RUFF_TARGETS)
	$(RUFF) format --check $(RUFF_TARGETS)
	$(PYTHON) -m pytest
	git diff --check

preflight:
	$(PYTHON) -m scripts.migration_preflight

verify-db:
	$(PYTHON) -m scripts.db_verify

run:
	$(PYTHON) -m bot
