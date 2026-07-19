---
name: project-application-layout-and-command-rules
description: Use before any Finance Harbour code change to understand the backend/frontend layout, Docker command rules, forbidden commands, and Django migration boundaries.
---

# Project Application Layout and Command Rules

Use this skill before any Finance Harbour task that edits code, runs commands, creates files, changes models, creates migrations, changes tests, or changes frontend/backend structure.

## Core rule

Finance Harbour is a Docker-based Django and React application.

Read `README.md`, `package.json`, `.githooks/**`, `.pre-commit-config.yaml`, and the relevant skill before choosing commands.

Use commands that actually exist in those files.

Do not invent commands.

Do not run host-machine validation commands when the repository provides Docker equivalents.

If another skill has a stricter rule, follow the stricter rule.

If the user prompt gives a narrower command list than this skill, follow the user prompt and do not run broader commands.

## Application layout

The repository root contains:

- `backend/` for Django backend code
- `frontend/` for React/Vite frontend code
- `.agents/skills/` for Codex skills
- `.claude/skills/` for Claude skills

The `.agents/skills/` and `.claude/skills/` folders must stay identical.

Do not add a skill to one folder without adding the exact same skill to the other folder.

Do not keep separate definition files beside skills.

Skill rules must live directly inside each `SKILL.md` file.

## Backend layout

Backend code lives under `backend/`.

Django apps live directly under `backend/<app_name>/`.

Existing app examples:

- `authentication/`
- `core/`
- `debt_profile/`
- `onboarding/`

Backend apps should follow this structure when the folder applies:

- `models/`
- `managers/`
- `serializers/`
- `structure_serializers/`
- `views/request_validators/`
- `api/views/`
- `api/viewsets/`
- `services/`
- `adapters/`
- `migrations/`
- `tests/`
- `urls.py`

Do not place backend domain code inside `config/`.

Do not place unrelated domain code inside `authentication/`.

## Backend model rules

Models must live inside the owning app.

Use this model file pattern:

- `backend/<app_name>/models/<model_name>.py`

Export models from:

- `backend/<app_name>/models/__init__.py`

New user-owned domain models must tie back to `settings.AUTH_USER_MODEL` through an explicit relationship unless the task explicitly defines a different ownership model.

Do not create orphaned user-owned records.

Do not use email strings as ownership.

Do not rely on frontend filtering for ownership protection.

## Django migration rules

Claude and Codex may create Django migration files when backend model changes require them.

Claude and Codex may run this Docker migration creation command when model changes require it:

- `docker compose exec -T backend python manage.py makemigrations <app_name>`

Use the owning app name.

Do not run broad `makemigrations` without an app name.

Inspect generated migration files before finishing.

Keep generated migrations in the owning app's `migrations/` folder.

Do not manually format migrations; Ruff excludes migrations.

Do not create migrations for frontend-only changes.

Do not create empty or data migrations unless the user explicitly asks.

Claude and Codex must not run migrations.

Forbidden migration/database commands include:

- `python manage.py migrate`
- `python manage.py migrate <app_name>`
- `python manage.py migrate <app_name> zero`
- `python manage.py sqlmigrate`
- `python manage.py dbshell`
- `python manage.py flush`
- `docker compose exec -T backend python manage.py migrate`
- `docker compose exec -T backend python manage.py migrate <app_name>`
- `docker compose exec -T backend python manage.py migrate <app_name> zero`
- `docker compose exec -T backend python manage.py sqlmigrate`
- `docker compose exec -T backend python manage.py dbshell`
- `docker compose exec -T backend python manage.py flush`
- any command that applies, rolls back, flushes, resets, or directly edits database schema/data outside a migration file

If migrations need to be applied or rolled back, stop and state that a human must run the migration command.

## Frontend layout

Frontend code lives under `frontend/`.

Frontend source lives under `frontend/src/`.

The frontend uses React, Vite, TypeScript, Tailwind, Yarn 4, ESLint, and Prettier.

Reusable UI belongs in `frontend/src/ui/`.

Route-level pages belong in `frontend/src/pages/`.

Large page-specific components belong in `frontend/src/components/pages/`.

Cross-cutting API/auth/service-container code belongs in `frontend/src/lib/`.

Do not put visual UI primitives in `lib/`.

Do not put API hooks directly inside visual components.

## Frontend commands

Run frontend validation through Docker from the project root.

Current Docker-compatible frontend validation commands from the Git hooks and package scripts:

- `docker compose run --rm --no-deps frontend yarn cleanup`
- `docker compose run --rm --no-deps frontend yarn check`
- `docker compose exec -T frontend yarn cleanup` when using the running container
- `docker compose exec -T frontend yarn check` when using the running container

Allowed frontend dependency commands from the README only when the user explicitly requests dependency changes:

- `cd frontend && yarn add package-name`
- `cd frontend && yarn add -D package-name`
- `docker compose restart frontend`

Do not run `yarn build:dev` unless the script exists and the user explicitly asks for it.

Do not run `npm`, `pnpm`, or `bun` commands.

Do not run host-machine frontend validation commands when Docker commands are available.

## Backend commands

Run backend validation through Docker from the project root.

Current backend check commands from the Git hooks and package configuration:

- `docker compose exec -T backend python manage.py check`
- `docker compose exec -T backend ruff check .`
- `docker compose exec -T backend ruff format --check .`

Current backend format command from the Git hooks:

- `docker compose exec -T backend ruff format .`

Current backend test commands supported by the Django project and Docker workflow:

- `docker compose exec -T backend python manage.py test`
- `docker compose exec -T backend python manage.py test <app_name>`

Current backend coverage commands from the pre-push workflow:

- `docker compose exec -T backend coverage run --source=. --omit="*/migrations/*,*/tests/*,manage.py,config/*" manage.py test`
- `docker compose exec -T backend coverage report -m`

Current backend migration creation command, only when migration creation is allowed:

- `docker compose exec -T backend python manage.py makemigrations <app_name>`

Use the narrowest backend test command that validates the changed behavior when the prompt asks for targeted tests.

Do not run broad backend tests when the user prompt provides an exact test class, exact app, or exact command.

## Dependency commands

Do not add, remove, upgrade, or lock dependencies unless the user explicitly asks for dependency changes.

Backend dependency commands from the README are allowed only when explicitly requested:

- `cd backend && PIPENV_VENV_IN_PROJECT=1 pipenv install package-name`
- `cd backend && PIPENV_VENV_IN_PROJECT=1 pipenv install --dev package-name`
- `cd backend && PIPENV_VENV_IN_PROJECT=1 pipenv lock && pipenv sync --dev`
- `docker compose up -d --build backend`

Frontend dependency commands from the README are allowed only when explicitly requested:

- `cd frontend && yarn add package-name`
- `cd frontend && yarn add -D package-name`
- `docker compose restart frontend`

## Forbidden commands

Do not run destructive or environment-changing commands unless the user explicitly gives that exact command.

Forbidden commands include:

- migration application commands listed in this skill
- migration rollback commands listed in this skill
- database reset, flush, shell, or direct data mutation commands listed in this skill
- package install/update/remove commands not explicitly requested
- commands that delete project files outside the task scope
- commands that rewrite git history
- commands that commit, push, merge, or rebase unless explicitly requested
- commands that modify secrets or environment files unless explicitly requested

## Completion rule

Before finishing a code task, verify:

- touched files are in the correct backend/frontend folder
- no forbidden commands were run
- migrations were created only when allowed
- migrations were not applied or rolled back
- `.agents/skills/` and `.claude/skills/` remain identical when skills were changed
- no definition files were added beside skills


## Mandatory repository discovery

Before creating files or abstractions:

- inspect the target and sibling files
- search existing call sites and analogous implementations
- for frontend work, use `frontend-component-reuse-and-composition`
- for backend work, inspect permissions, owner scoping, request validators, response serializers, constraints, query access, and transaction boundaries
- use `repository-grounded-change-completion` before reporting completion

Do not add a component, hook, service, Django app, dependency, or command based only on a general best practice. It must fit the actual repository and task.
