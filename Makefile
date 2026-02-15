.PHONY: openapi backend frontend build up up-dev up-prod down

# Generate OpenAPI JSON
openapi:
	@echo "Generating OpenAPI JSON..."
	python backend/app/utilities/openapi.py
	@echo "OpenAPI JSON generated!"

# Build backend image only
backend:
	@echo "Building Backend..."
	docker build -t invoice-backend ./backend
	@echo "Backend Built!"

# Build frontend image only (depends on OpenAPI)
frontend: openapi
	@echo "Building Frontend..."
	docker build -t invoice-frontend ./frontend
	@echo "Frontend Built!"

# Build both backend and frontend
build: backend frontend
	@echo "All images built!"

# Development environment (live reload & Vite dev)
up-dev: openapi
	docker compose -f docker-compose.yml up --build

# Production environment (Nginx + backend)
up-prod: openapi
	docker compose -f docker-compose.prod.yml up --build -d

# Build everything and start (default)
up: build
	docker compose up

# Stop containers
down:
	docker compose down
