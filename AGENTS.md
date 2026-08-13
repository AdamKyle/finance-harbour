# Finance Harbour Agent Instructions

These instructions apply to this repository.

## Project facts from the current codebase

- The backend is a Django REST Framework app under `backend/`.
- The active backend Django apps are `authentication`, `core`, `onboarding`, and `debt_profile`.
- Backend apps use responsibility-specific folders such as `models/`, `managers/`, `serializers/`, `structure_serializers/`, `views/request_validators/`, `api/views/`, `api/viewsets/`, `services/`, `adapters/`, `urls.py`, and mirrored tests when those responsibilities apply.
- The backend uses `dj-rest-auth`, `django-allauth`, `djangorestframework-simplejwt`, JWT cookies, CSRF protection, throttling, PostgreSQL, and Ruff.
- The frontend is React 19, TypeScript, Vite, React Router 7, Tailwind CSS, tsyringe, axios, strict `tsconfig`, ESLint, Prettier, and Yarn 4.
- Frontend source lives under `frontend/src/` with aliases for `assets`, `components`, `configuration`, `layout`, `lib`, `pages`, `router`, `styles`, `ui`, and `util`.
- The frontend uses reusable `ui/**` components, page-specific `components/pages/**`, app services under `lib/**`, route files under `react-router/**`, and colocated `types/**`, `definitions/**`, or existing `deffinitions/**` files. Preserve the current `deffinitions` spelling where it already exists.

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
- Frontend component discovery/reuse: `.agents/skills/frontend-component-reuse-and-composition/SKILL.md`
- Frontend behavior verification: `.agents/skills/frontend-behavioral-validation/SKILL.md`
- Frontend import aliases: `.agents/skills/frontend-import-aliases/SKILL.md`
- Frontend Event System: `.agents/skills/frontend-event-system/SKILL.md`
- Frontend Side Peeks: `.agents/skills/frontend-side-peeks/SKILL.md`
- Frontend browser-global access: `.agents/skills/frontend-browser-global-access/SKILL.md`
- Backend security and SOC 2 control support: `.agents/skills/backend-security-and-soc2-controls/SKILL.md`
- Backend database efficiency: `.agents/skills/backend-database-performance-and-efficiency/SKILL.md`
- Backend transactions/concurrency/idempotency: `.agents/skills/backend-transactions-concurrency-and-idempotency/SKILL.md`
- Completion evidence: `.agents/skills/repository-grounded-change-completion/SKILL.md`

## Global rules

- Do not include `.env` values in code, docs, prompts, commits, examples, generated zips, or responses.
- Do not guess missing architecture. Inspect the current files first.
- Keep changes consistent with the existing folder structure and naming already present in this repo.
- Prefer small focused changes over broad rewrites.
- Inspect the target code, sibling files, call sites, analogous implementations, and tests before writing code.
- For frontend work, search and reuse the existing `ui/**` and feature components before writing JSX. Do not invent a parallel component or raw duplicate control.
- Do not create speculative abstractions. Extract only for a concrete reused or distinct responsibility supported by the current code.
- Every API class must explicitly declare permissions; user-owned queries and writes must be scoped from `request.user` or an owner-derived relationship.
- Treat authentication and financial data as sensitive. Do not log full payloads or expose fields outside explicit response serializers.
- Do not claim SOC 2 compliance, security, performance, or test completion without direct evidence.
- Add or update tests for backend behavior changes.
- New backend domain work must be implemented as a separate Django app unless it is strictly authentication-specific.
- New backend domain data must tie back to `authentication.User` through ownership, creator, membership, or another explicit user relationship.
- Do not add mocks to make backend tests pass. Backend tests must exercise real code paths and the test database.
- Do not expose raw JWT `access` or `refresh` tokens in frontend or backend response bodies.
- Preserve the cookie-only auth contract unless a task explicitly changes authentication design.

## Commands

Run project validation through Docker from the repository root, matching the current Git hooks and project command skill.

Backend checks:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend ruff check .
docker compose exec -T backend ruff format --check .
docker compose exec -T backend coverage run --source=. --omit="*/migrations/*,*/tests/*,manage.py,config/*" manage.py test
docker compose exec -T backend coverage report -m
```

Frontend cleanup:

```bash
docker compose run --rm --no-deps frontend yarn cleanup
```

Full frontend check:

```bash
docker compose run --rm --no-deps frontend yarn check
```

Use a narrower test or check when the user supplies an exact command or the task requires only a targeted validation. Do not run migrations.
