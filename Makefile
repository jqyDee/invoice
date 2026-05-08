.PHONY: openapi up-dev up-prod down db-migrate db-upgrade db-downgrade db-current backend-test format lint lint-fix frontend-lint frontend-build

# Development environment (live reload & Vite dev)
up-dev: openapi
	docker compose -f docker-compose.yml up --build

# Generate OpenAPI JSON
openapi:
	@echo "$@: \t ---------------"
	@echo "$@: \t Generating OpenAPI JSON..."
	python backend/app/utilities/openapi.py
	@echo "$@: \t OpenAPI JSON generated!"
	@echo "$@: \t ---------------"

# Production environment
up-prod:
	docker compose -f docker-compose.prod.yml up -d

# Stop containers
down:
	docker compose down || docker compose -f docker-compose.prod.yml down

# Generate a new migration
db-migrate:
ifndef m
	$(error m is required - usage: make db-migrate m="describe_change")
endif
	cd backend && alembic -c app/alembic.ini revision --autogenerate -m "$(m)"

# Apply all pending migrations
db-upgrade:
	cd backend && alembic -c app/alembic.ini upgrade head

# Roll back one migration
db-downgrade:
	cd backend && alembic -c app/alembic.ini downgrade -1

# Show current revision
db-current:
	cd backend && alembic -c app/alembic.ini current

backend-test:
	cd backend && pytest

# Format backend code
format:
	cd backend && ruff format .

# Lint backend code
lint:
	cd backend && ruff check .

# Lint + auto-fix
lint-fix:
	cd backend && ruff check --fix .

# Lint frontend code
frontend-lint:
	cd frontend && npm run lint

# Type-check + build frontend
frontend-build:
	cd frontend && npm run build

check: format lint-fix frontend-lint frontend-build backend-test
	@echo Done
