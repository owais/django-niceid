.DEFAULT_GOAL := help

.PHONY: help install sync build test test-postgres test-all lint format format-check check migrate postgres-up postgres-down clean

export PATH := $(HOME)/.local/bin:$(PATH)
UV ?= $(shell command -v uv 2>/dev/null || echo uv)
POSTGRES_HOST ?= localhost
POSTGRES_PORT ?= 54329
export POSTGRES_HOST POSTGRES_PORT

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install sync: ## Install dev dependencies (uv sync --extra dev)
	$(UV) sync --extra dev

build: ## Build sdist and wheel (uv build)
	$(UV) build

lint: ## Run ruff linter
	$(UV) run ruff check .

format: ## Format code with ruff
	$(UV) run ruff format .

format-check: ## Verify formatting without writing
	$(UV) run ruff format --check .

test: ## Run unit tests (excludes PostgreSQL)
	$(UV) run pytest -m "not postgres"

migrate: ## Apply test project migrations
	$(UV) run python -m django migrate --settings=testproj.settings

postgres-up: ## Start PostgreSQL (docker compose)
	docker compose up -d --wait

postgres-down: ## Stop PostgreSQL
	docker compose down

test-postgres: postgres-up migrate ## Run PostgreSQL integration tests
	$(UV) run pytest -m postgres

test-all: test test-postgres ## Run all tests

check: lint format-check test ## Lint, format check, and unit tests (CI-like)

clean: ## Remove build artifacts and caches
	rm -rf dist build .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
