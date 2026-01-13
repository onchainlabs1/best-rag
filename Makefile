.PHONY: help install test lint format type-check docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Run type checking"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make clean        - Clean generated files"

install:
	cd backend && poetry install

test:
	cd backend && poetry run pytest

lint:
	cd backend && poetry run ruff check src tests

format:
	cd backend && poetry run ruff format src tests

type-check:
	cd backend && poetry run mypy src

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

dev:
	@./scripts/dev.sh

test-local:
	@./scripts/test-local.sh

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .mypy_cache -exec rm -r {} +
	find . -type d -name .ruff_cache -exec rm -r {} +
	rm -rf .coverage htmlcov dist build *.egg-info
