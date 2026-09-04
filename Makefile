PYTHON ?= python3

.PHONY: install-backend test run-backend db-up

install-backend:
	$(PYTHON) -m pip install -e ./backend

test:
	$(PYTHON) -m pytest backend/tests -q

run-backend:
	$(PYTHON) -m uvicorn app.main:app --reload --app-dir backend

db-up:
	docker compose up -d postgres
