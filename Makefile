SHELL := /bin/bash
.PHONY: up down db-up db-down migrate migrate-manual backend frontend install-backend install-frontend test

# run everything (db + backend + frontend)
up:
	docker compose up --build

# stop everything
down:
	docker compose down

# spin up postgres only
db-up:
	docker compose up db -d

# stop postgres only
db-down:
	docker compose down

# run alembic migrations
migrate-manual:
	cd backend && . venv/bin/activate && alembic upgrade head

# auto-generate a new migration
migrate:
	cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

# run backend dev server
backend:
	cd backend && . venv/bin/activate && python run.py

# run frontend dev server
frontend:
	cd frontend && npm run dev

# install backend dependencies
install-backend:
	cd backend && . venv/bin/activate && pip install -r requirements.txt

# install frontend dependencies
install-frontend:
	cd frontend && npm install

# run backend tests
test:
	cd backend && . venv/bin/activate && python -m pytest tests/ -v
