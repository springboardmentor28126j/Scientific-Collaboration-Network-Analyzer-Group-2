.PHONY: help up down build restart logs logs-app logs-db ps shell \
        migrate makemigrations migrate-down test test-cov lint format \
        typecheck check clean db-shell db-reset \
        venv install sync lint-local format-local typecheck-local \
        test-local test-local-cov check-local run-local

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

## --- Docker lifecycle ---

up: ## Start backend, frontend, database, and mailcatcher
	docker compose up --build

up-d: ## Start all services in the background
	docker compose up --build -d

down: ## Stop all services
	docker compose down

down-v: ## Stop all services AND wipe volumes (fresh db/mailcatcher state)
	docker compose down -v

restart: ## Restart just the app container
	docker compose restart app

build: ## Rebuild the app image without starting anything
	docker compose build

ps: ## Show running containers
	docker compose ps

## --- Logs ---

logs: ## Tail logs for all services
	docker compose logs -f

logs-app: ## Tail logs for the app only
	docker compose logs -f app

logs-db: ## Tail logs for postgres only
	docker compose logs -f db

## --- Shells ---

shell: ## Open a bash shell inside the running app container
	docker compose exec app bash

db-shell: ## Open a psql shell inside the running db container
	docker compose exec db psql -U postgres -d research_db

## --- Database / migrations (via Docker) ---

migrate: ## Apply all pending Alembic migrations
	docker compose exec app alembic upgrade head

makemigrations: ## Autogenerate a new migration (usage: make makemigrations m="add papers table")
	docker compose exec app alembic revision --autogenerate -m "$(m)"

migrate-down: ## Roll back the last migration
	docker compose exec app alembic downgrade -1

db-reset: ## DESTROYS the db volume and re-runs migrations from scratch
	docker compose down -v
	docker compose up -d db mailcatcher
	docker compose run --rm app alembic upgrade head

## --- Testing / quality (via Docker) ---

test: ## Run the test suite inside Docker
	docker compose exec app pytest

test-cov: ## Run tests with coverage report inside Docker
	docker compose exec app pytest --cov=app --cov-report=term-missing

lint: ## Run ruff lint checks inside Docker
	docker compose exec app ruff check app tests

format: ## Auto-format code with ruff inside Docker
	docker compose exec app ruff format app tests

typecheck: ## Run mypy type checks inside Docker
	docker compose exec app mypy app

check: lint typecheck test ## Run lint + typecheck + tests together (Docker)

## --- Cleanup ---

clean: ## Remove containers, volumes, and dangling images for this project
	docker compose down -v --rmi local

## --- Local (non-Docker) dev environment, via uv ---

venv: ## Create a local virtualenv at .venv using uv
	uv venv .venv

install: ## Install project + dev dependencies into .venv (creates .venv if missing)
	uv venv .venv --allow-existing
	uv pip install --python .venv/bin/python -e ".[dev]"
	uv pip install --python .venv/bin/python "bcrypt==4.0.1"

sync: ## Re-sync .venv to exactly match pyproject.toml (removes anything extra)
	uv sync --extra dev
	uv pip install --python .venv/bin/python "bcrypt==4.0.1"

lint-local: ## Run ruff lint checks locally (no Docker)
	.venv/bin/ruff check app tests

format-local: ## Auto-format code with ruff locally (no Docker)
	.venv/bin/ruff format app tests

typecheck-local: ## Run mypy locally (no Docker)
	.venv/bin/mypy app

test-local: ## Run the test suite locally (no Docker, uses in-memory SQLite)
	.venv/bin/pytest

test-local-cov: ## Run tests with coverage locally (no Docker)
	.venv/bin/pytest --cov=app --cov-report=term-missing

check-local: lint-local typecheck-local test-local ## Run lint + typecheck + tests together (local)

run-local: ## Run the app locally with uvicorn (needs local Postgres/Mailcatcher or a local .env pointing elsewhere)
	.venv/bin/uvicorn app.main:app --reload
