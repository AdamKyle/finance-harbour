# Finance Harbour Agent Instructions

These instructions apply to this repository.

## Project facts from the current codebase

- The backend is a Django REST Framework app under `backend/`.
- The active backend Django app is `authentication`.
- Backend app code is split into `models/`, `managers/`, `serializers/`, `api/views/`, `api/viewsets/`, `adapters/`, `urls.py`, and mirrored tests under `tests/`.
- The backend uses `dj-rest-auth`, `django-allauth`, `djangorestframework-simplejwt`, JWT cookies, CSRF protection, throttling, PostgreSQL, and Ruff.
- The frontend is React 19, TypeScript, Vite, React Router 7, Tailwind CSS, tsyringe, axios, strict `tsconfig`, ESLint, Prettier, and Yarn 4.
- Frontend source lives under `frontend/src/` with aliases for `assets`, `components`, `configuration`, `layout`, `lib`, `pages`, `router`, `styles`, and `ui`.
- The frontend uses reusable `ui/**` components, page-specific `components/pages/**`, app services under `lib/**`, route files under `react-router/**`, and colocated `types/**` or `definitions/**` files.

## Required skill usage

Use the matching skill before changing code:

- Backend structure and app ownership: `.agents/skills/backend-architecture/SKILL.md`
- Backend tests and coverage: `.agents/skills/backend-testing/SKILL.md`
- Backend Ruff and formatting: `.agents/skills/backend-formatting/SKILL.md`
- Backend auth/API contracts: `.agents/skills/backend-api-contracts/SKILL.md`
- Frontend structure: `.agents/skills/frontend-architecture/SKILL.md`
- Frontend components: `.agents/skills/frontend-components/SKILL.md`
- Frontend types/interfaces: `.agents/skills/frontend-types/SKILL.md`
- Frontend API hooks/context/service container: `.agents/skills/frontend-api-hooks/SKILL.md`
- Frontend formatting/checks: `.agents/skills/frontend-formatting/SKILL.md`

## Global rules

- Do not include `.env` values in code, docs, prompts, commits, examples, generated zips, or responses.
- Do not guess missing architecture. Inspect the current files first.
- Keep changes consistent with the existing folder structure and naming already present in this repo.
- Prefer small focused changes over broad rewrites.
- Add or update tests for backend behavior changes.
- New backend domain work must be implemented as a separate Django app unless it is strictly authentication-specific.
- New backend domain data must tie back to `authentication.User` through ownership, creator, membership, or another explicit user relationship.
- Do not add mocks to make backend tests pass. Backend tests must exercise real code paths and the test database.
- Do not expose raw JWT `access` or `refresh` tokens in frontend or backend response bodies.
- Preserve the cookie-only auth contract unless a task explicitly changes authentication design.

## Commands

Backend checks:

```bash
cd backend
ruff check .
ruff format --check .
coverage run --source=. --omit="*/migrations/*,*/tests/*,manage.py,config/*" manage.py test
coverage report -m
```

Frontend checks:

```bash
cd frontend
yarn cleanup
yarn lint
yarn type-check
yarn unused-files-check
yarn build
```

Full frontend check:

```bash
cd frontend
yarn check
```
