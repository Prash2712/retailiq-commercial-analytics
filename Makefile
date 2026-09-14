PYTHON ?= python

.PHONY: install test lint ingest profile

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

ingest:
	retailiq ingest

profile:
	retailiq profile
