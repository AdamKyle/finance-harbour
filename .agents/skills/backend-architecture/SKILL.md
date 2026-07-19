---
name: backend-architecture
description: Use when adding or changing Django apps, models, managers, serializers, URLs, settings, or backend folder structure in Finance Harbour.
---

# Backend Architecture Skill

Use this skill for backend structure, Django app boundaries, model ownership, managers, serializers, settings, migrations, and URLs.

## Non-negotiable rules

- New backend domain work must be a separate Django app unless it is strictly authentication-specific.
- Every new domain app must tie data back to `authentication.User` through explicit ownership, creator, membership, or another user relationship.
- Do not add unrelated domain behavior to the existing `authentication` app.
- Preserve the current app layout style: `models/`, `managers/`, `serializers/`, `api/views/`, `api/viewsets/`, `adapters/`, `urls.py`, and mirrored tests.
- Add new apps to `INSTALLED_APPS` under the existing `# Core Apps` section.
- Keep API routes under the root `/api/` include pattern from `config/urls.py`.

## Required checks and command boundaries

Use the project command rules before running backend commands.

After backend architecture changes, use the narrowest command set that validates the task.

Default backend validation, when the user has not provided a narrower command, is run through Docker from the project root:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend ruff check .
docker compose exec -T backend ruff format --check .
docker compose exec -T backend coverage run --source=. --omit="*/migrations/*,*/tests/*,manage.py,config/*" manage.py test
docker compose exec -T backend coverage report -m
```

If the prompt gives an exact backend test filter or exact command, run only that narrower command.

Do not run `python manage.py migrate`.

Do not run any command that applies migrations or directly changes the database schema/data.

## Backend Architecture Definition

### Current backend structure

The backend lives under `backend/`.

Observed project files and apps:

```text
backend/
  manage.py
  pyproject.toml
  Pipfile
  Pipfile.lock
  config/
  authentication/
  core/
  onboarding/
  debt_profile/
```

The active domain architecture is not authentication-only. Inspect the owning app before placing code.

### Current app pattern

The `authentication` app is structured by responsibility:

```text
authentication/models/user.py
authentication/managers/user_manager.py
authentication/serializers/register_serializer.py
authentication/serializers/user_details_serializer.py
authentication/api/views/*.py
authentication/api/viewsets/*.py
authentication/adapters/social_account_adapter.py
authentication/urls.py
```

Use the combined patterns from `authentication`, `core`, `onboarding`, and `debt_profile`; only create folders that the app responsibility actually needs.

### Concrete new app creation rules

When creating a new Django app:

1. Create the app under `backend/<app_name>/`.
2. Add `apps.py` using the app's config class.
3. Add the app to `INSTALLED_APPS` under the existing `# Core Apps` section.
4. Add app-local `urls.py` when the app exposes API routes.
5. Include app URLs under the root `/api/` routing pattern.
6. Place models under `models/<model_name>.py`.
7. Export models through `models/__init__.py` when the model is imported elsewhere.
8. Place serializers under `serializers/` or `structure_serializers/` based on the response contract.
9. Place views/viewsets under `api/views/` or `api/viewsets/`.
10. Place domain services under `services/`.
11. Mirror tests under `tests/` using the same app structure.
12. Create migrations only when model changes require them.
13. Do not run migrations.

### New Django app rules

When adding a new backend feature that is not strictly authentication behavior:

1. Create a new Django app.
2. Keep that app focused on one domain.
3. Add the app to `INSTALLED_APPS` under `# Core Apps`.
4. Add app-local `urls.py` and include it from `config/urls.py` or the current API routing pattern.
5. Add models in `app_name/models/<model_name>.py`.
6. Export models through `app_name/models/__init__.py` when needed.
7. Add serializers in `app_name/serializers/`.
8. Add API views/viewsets under `app_name/api/views/` or `app_name/api/viewsets/`.
9. Mirror tests under `app_name/tests/` using the same folder shape.
10. Add migrations generated from real model changes.

### Migration rules

Models may be created or changed when the task requires backend data structure changes.

Migrations may be created when model changes require them.

Allowed migration creation command from the repository root:

```bash
docker compose exec -T backend python manage.py makemigrations <app_name>
```

Rules:

- Create migrations only from real backend model changes.
- Use app-scoped `makemigrations <app_name>` instead of broad `makemigrations`.
- Inspect generated migration files before finishing.
- Keep generated migrations in the owning app's `migrations/` folder.
- Do not manually format migrations; Ruff excludes migrations.
- Do not create migrations for frontend-only changes.
- Do not create empty/data migrations unless the user explicitly asks.
- Do not run `python manage.py migrate`.
- Do not run Docker migrate equivalents.
- Do not run `dbshell`, `flush`, or commands that directly mutate database schema/data.

If a migration needs to be applied, stop after creating the migration file and state that a human must run migrations.

### User ownership rules

Every new domain model that stores user-owned data must explicitly tie back to `authentication.User`.

Accepted ownership patterns:

```python
user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="...",
)
```

or an explicit relationship model when data is shared between users.

Rules:

- Do not create orphaned domain records.
- Do not rely on email strings as ownership.
- Do not rely on frontend filtering for ownership protection.
- Filter queryset access by the authenticated user at the backend boundary.
- Test that one user cannot read or mutate another user’s data.

### Model rules

Follow the current model style from `authentication.models.user.User`:

- Use explicit field defaults.
- Use database constraints for data invariants when possible.
- Keep normalization in model/manager methods when persistence must enforce it.
- Prefer case-insensitive uniqueness constraints where identity fields require it.
- Avoid adding nullable fields unless the domain requires a true unknown state.

### Manager rules

Follow `authentication.managers.user_manager.UserManager`:

- Keep object creation logic in managers when it enforces model invariants.
- Normalize/validate before saving.
- Raise explicit exceptions for invalid required fields.

### Serializer rules

Follow the current serializer pattern:

- Use `ModelSerializer` for model-backed response shapes.
- Keep read-only fields explicit for user details and derived auth payloads.
- Validate duplicate/user-owned data in serializers when the API boundary needs it.
- Do not expose secrets, raw tokens, passwords, or internal-only fields.

### Settings rules

Current settings read required secrets from environment variables:

```python
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
SIMPLE_JWT = {
    "SIGNING_KEY": os.environ["SIMPLE_JWT_SIGNING_KEY"],
}
```

Rules:

- Do not hardcode secrets.
- Do not add fallback production secrets.
- Do not expose Google OAuth secret to frontend code.
- Preserve `AUTH_USER_MODEL = "authentication.User"`.
- Preserve secure cookie and CSRF defaults unless the task explicitly changes auth design.

### API routing rules

Current API root:

```python
urlpatterns = [
    path("api/", include("authentication.urls")),
    path("api/", include("onboarding.urls")),
    path("api/", include("debt_profile.urls")),
]
```

Rules:

- Keep endpoints under `/api/`.
- Use app-local `urls.py`.
- Use DRF routers for viewsets when resource routes are appropriate.
- Use explicit `path()` entries for action endpoints like login/registration/social login.

## Request validator architecture

Use the `backend-request-validators` skill when validating backend request payloads.

Request payload validation belongs in request validator classes under `<app_name>/views/request_validators/`.

The shared request validation engine belongs in `core/request_validator_engine/engine.py`.

Use structure serializers for response/output shape.

Do not use response serializers as request object validators when a request validator is the correct boundary.

## Unique field architecture

Use the `backend-unique-fields` skill when adding name-like or identity-like fields to models.

Name-like fields must be unique at the correct scope unless the task explicitly allows duplicates.

Optional unique string fields must use conditional constraints when multiple blank values are valid.



## Security, efficiency, and consistency gates

For backend architecture changes also use:

- `backend-security-and-soc2-controls`
- `backend-database-performance-and-efficiency`
- `backend-transactions-concurrency-and-idempotency`
- `repository-grounded-change-completion`

Every API class must explicitly declare permissions because the current settings do not define a global default permission class.

Every user-owned query must start from `request.user` or an owner-derived relation. Every response must use an explicit serializer contract. Multi-record mutations require an explicit transaction decision, and collection/query changes require a concrete bounded-query decision.
