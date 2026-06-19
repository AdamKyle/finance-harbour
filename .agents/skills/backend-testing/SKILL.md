---
name: backend-testing
description: Use when adding or changing Django unit tests, API tests, coverage rules, auth tests, or test fixtures in Finance Harbour.
---

# Backend Testing Skill

Use this skill for all backend test changes.

## Non-negotiable rules

- Backend behavior must have unit/API tests.
- Coverage target is 100% for backend app source.
- Do not add mocks, patches, or fake pass-through behavior to make tests pass.
- Tests must exercise the real Django code path and the test database.
- For user-owned data, test that ownership boundaries are enforced.
- For auth changes, test cookies, CSRF, throttling, and response bodies.

## Existing test style

The codebase currently uses:

- `django.test.TestCase`
- `rest_framework.test.APITestCase`
- `rest_framework.test.APIClient`
- `django.test.RequestFactory`
- `override_settings` for settings-specific behavior
- `coverage run ... manage.py test`

## Required command and command boundaries

Use the project command rules before running backend test commands.

Default backend test validation, when the user has not provided a narrower command, is:

```bash
cd backend
coverage run --source=. --omit="*/migrations/*,*/tests/*,manage.py,config/*" manage.py test
coverage report -m
```

If the prompt gives an exact backend test class, exact filter, or exact command, run only that narrower command.

Do not run `python manage.py migrate` before tests.

Do not run commands that apply migrations or directly mutate database schema/data.

## Backend Testing Definition

### Current backend test layout

Tests mirror the backend app structure:

```text
authentication/tests/
  adapters/test_social_account_adapter.py
  api/test_auth_throttling.py
  api/views/test_auth_response.py
  api/views/test_google_login_view.py
  api/views/test_register_view.py
  api/viewsets/test_csrf_cookie_viewset.py
  auth/test_dj_rest_auth_cookie_auth.py
  managers/test_user_manager.py
  models/test_user.py
  serializers/test_user_details_serializer.py
  settings/test_jwt_settings.py
  settings/test_security_settings.py
```

New apps must follow the same mirrored test structure.

### Coverage rule

The CI command omits migrations, tests, `manage.py`, and `config/*`:

```bash
coverage run   --source=.   --omit="*/migrations/*,*/tests/*,manage.py,config/*"   manage.py test
coverage report -m
```

Rules:

- The expected standard is 100% coverage for app source included by this command.
- Do not lower the standard.
- Do not exclude app files just to hide missing tests.
- Do not move behavior into `config/*` to avoid coverage.
- Every branch introduced by new code must be tested.

### Mocking rule

User requirement: backend tests must not rely on mocks to let behavior fall through or fake success.

Rules:

- Do not add `unittest.mock.patch` for application behavior.
- Do not mock managers, serializers, models, viewsets, permissions, or API clients to bypass the real code path.
- Do not assert only that a mock was called.
- Use the real Django test database.
- Use real model instances through managers when the production path uses managers.
- Use `APIClient` for endpoint contracts.
- Use `RequestFactory` only for narrow request/response helper tests where a full API request is not the behavior under test.
- Use `override_settings` only when the behavior being tested is settings-driven.

If an external provider is involved, keep the boundary small and test the app-owned logic directly. Do not fake a successful backend path that production code would not execute.

### API test rules

For DRF endpoints:

- Use `APITestCase`.
- Use `APIClient(enforce_csrf_checks=True)` when testing authenticated unsafe requests.
- Pass `secure=True` for secure-cookie/CSRF behavior.
- Use `HTTP_X_CSRFTOKEN` and `HTTP_ORIGIN` when matching auth flows.
- Assert status codes using `rest_framework.status`.
- Assert response body shape.
- Assert database state.
- Assert forbidden/unauthorized behavior, not only success behavior.

### Auth-specific tests

Current auth tests verify:

- Registration sets JWT cookies.
- Login sets JWT cookies.
- Logout deletes JWT cookies.
- Session and messages cookies are removed from auth responses.
- Raw `access` and `refresh` tokens are removed from response bodies.
- `/api/auth/user/` returns `completed_onboarding`.
- CSRF is required for registration/login/logout.
- CSRF endpoint sets cookie and returns token.
- Auth endpoints are throttled.
- Duplicate email registration is rejected case-insensitively.
- Password validation rejects weak passwords.
- JWT signing key is separate from Django secret key.
- Security settings match debug mode.

Any auth change must preserve or update these tests.

### User ownership tests

For any new user-owned model/API, add tests for:

1. Authenticated user can create/read/update/delete their own record when allowed.
2. Another authenticated user cannot access or mutate that record.
3. Anonymous users are rejected when auth is required.
4. Querysets are filtered by `request.user`.
5. Serializer output does not leak another user’s data.

### Model tests

For models:

- Test database constraints, not just serializer validation.
- Use `transaction.atomic()` around expected `IntegrityError` cases.
- Test normalization on save and manager creation when applicable.
- Test required ownership relationships.

### Serializer tests

For serializers:

- Test exact output fields.
- Test read-only fields.
- Test validation errors.
- Test duplicate/user-owned constraints at the serializer boundary when relevant.

### Settings tests

Settings tests should assert security-sensitive configuration directly, as the current repo does for:

- `SIMPLE_JWT["SIGNING_KEY"]`
- cookie security flags
- SSL/HSTS behavior
- security headers
- proxy SSL header

### Naming rules

- Test files must be named `test_<thing>.py`.
- Test classes must end with `Test`.
- Test methods must start with `test_` and describe behavior.
- Prefer behavior names, e.g. `test_registration_rejects_duplicate_email`.

## One test class per file

Use the `backend-test-class-file-structure` skill when editing backend tests.

Each backend test class must live in its own test file.

Do not place multiple test classes in one test file.

Split existing mixed test files when touched by the task.

