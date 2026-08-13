# Finance Harbour

Finance Harbour is a personal budget planning app built with Django REST Framework, PostgreSQL, React, TypeScript, Tailwind CSS, Vite, Yarn, and Docker.

## Repository access and commands

Edit and inspect repository files directly through workspace access. Docker is for established project commands, not for reading or searching mounted source.

Do not create a host virtual environment or use host Pipenv, Python, Ruff, Yarn, or npm for repository work. A dependency change requires explicit user authorization and a Docker-based command established for that task.

Do not run migrations, migration generation, database clients, database probes, or database-backed tests unless a later task explicitly authorizes the exact action.

## Setup and development

Copy `.env.example` to `.env`, provide local values, and keep `.env` uncommitted. Do not place secrets in source, documentation, prompts, or generated artifacts.

The application services are defined in `docker-compose.yml`. Source files are mounted into the existing backend and frontend services for development.

Normal source changes should reload through the running development services. Dependency changes are not part of ordinary source work and are not authorized by default.

## Application URLs

The local frontend is served at the frontend URL configured by the project environment. The backend health endpoint is available at `/api/health/` on the configured backend origin.

Google OAuth configuration must keep the provider secret backend-only. The backend and frontend client identifiers must correspond, and configured callback values must match the provider configuration.

## Static validation

Run repository validation through the existing Docker Compose services from the repository root.

Frontend:

```bash
docker compose exec -T frontend yarn cleanup
docker compose exec -T frontend yarn check
```

Backend static lint and formatting checks:

```bash
docker compose exec -T backend ruff check .
docker compose exec -T backend ruff format --check .
```

When backend formatting is required:

```bash
docker compose exec -T backend ruff format .
docker compose exec -T backend ruff check .
docker compose exec -T backend ruff format --check .
```

Use the narrowest command set authorized by the current task. Do not substitute host tooling when Docker equivalents exist.

