# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack invoice management system for healthcare/therapy practices (Heilpraktiker, Physiotherapy). Built with FastAPI (Python) + React/TypeScript, containerized with Docker.

## Common Commands

**Development:**
```bash
make up-dev          # Start dev environment with hot-reload (runs openapi generation first)
make down            # Stop containers
```

**OpenAPI / API Client:**
```bash
make openapi                            # Regenerate openapi.json from backend
cd frontend && npm run openapi-ts:generate  # Regenerate frontend API client from openapi.json
```
> Always run `make openapi` after backend model/schema/router changes, then regenerate the frontend client.

**Database Migrations:**
```bash
make db-migrate m="describe_change"  # Create new Alembic migration (autogenerate)
make db-upgrade                       # Apply pending migrations
make db-downgrade                     # Roll back one migration
make db-current                       # Show current revision
```

**Backend Tests:**
```bash
cd backend && pip install -e ".[dev]"
pytest                    # All tests with coverage
pytest tests/path/to/test_file.py::test_name  # Single test
```

**Frontend Linting / Build:**
```bash
cd frontend && npm run lint    # ESLint
cd frontend && npm run build   # Type-check + production build
```

## Architecture

### Backend (`backend/app/`)

**Pattern:** Router → Service → Model/Schema

- `routers/` — HTTP endpoints; each router calls into `services/`
- `services/` — Business logic; no HTTP concerns
- `schemas/` — Pydantic models for request/response validation
- `models/` — SQLAlchemy ORM models
- `pdf/` — PDF generation (fpdf2); separate classes per document type (`invoice_pdf.py`, `invoice_hp_pdf.py`, `invoice_kg_pdf.py`, `therapy_pdf.py`, `privacy_pdf.py`)
- `utilities/` — Config, DB session factory, JWT security, logger, seed, OpenAPI generation

**Auto-router registration:** `utilities/router_include.py` dynamically discovers and registers all modules that expose an `APIRouter` as `router`.

**Database:** SQLite at `/app/data/db.db`, managed by SQLAlchemy + Alembic. Migrations run automatically on container startup (`alembic upgrade head`).

**Auth:** JWT Bearer tokens (HS256), bcrypt passwords, OAuth2 scheme via FastAPI's `Depends()`.

### Frontend (`frontend/src/`)

**Pattern:** Auto-generated API client → TanStack React Query → React components

- `api/` — **Auto-generated** from `openapi.json` via `@hey-api/openapi-ts`. Do not edit manually.
- `components/` — Feature-organized React components (`invoice/`, `invoice-edit/`, `patient/`, `settings/`, `layouts/`)
- `contexts/` — `auth-context.tsx` (JWT state, login/logout), `toast-provider.tsx`
- `hooks/invoice/` — Invoice-specific custom hooks
- `utilities/` — Shared helpers (date formatting, status/gender enum maps, PDF preview, total calculation)
- `config/` — Route definitions and app configuration

**Routing:** React Router v7 with protected routes. `ProtectedRoute` wraps authenticated pages. Route definitions live in `config/routes.ts`.

**UI:** PrimeReact component library (`mdc-light-indigo` theme) + PrimeFlex CSS utilities.

**API proxy:** Vite proxies `/api/*` to `${BACKEND_URL}` (set via Docker environment).

### Infrastructure

- Dev: `docker-compose.yml` — source-mounted volumes for hot-reload on both backend (uvicorn `--reload`) and frontend (Vite HMR)
- Prod: `docker-compose.prod.yml` — pulls images from GHCR, Nginx serves frontend static files, Watchtower auto-updates
- CI/CD: GitHub Actions runs `pytest` on PRs to main; builds/pushes Docker images on version tags (`v*.*.*`); Release-Please automates versioning and changelog