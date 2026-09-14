PYTHON ?= python

.PHONY: install test lint ingest profile db-up db-down warehouse-build reconcile

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

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

warehouse-build:
	retailiq warehouse-build

reconcile:
	retailiq reconcile
