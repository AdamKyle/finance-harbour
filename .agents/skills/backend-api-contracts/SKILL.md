---
name: backend-api-contracts
description: Use when changing backend auth, DRF endpoints, JWT cookies, CSRF, throttling, serializers, or response contracts in Finance Harbour.
---

# Backend API Contracts Skill

Use this skill for backend API endpoints, auth flows, response payloads, cookies, CSRF, throttling, and serializer contracts.

## Non-negotiable auth contract

- JWT auth is cookie-based.
- Do not return raw `access` or `refresh` tokens in response bodies.
- Preserve CSRF protection for unsafe requests.
- Preserve auth throttling scopes unless explicitly changed.
- Keep Google OAuth secret backend-only.
- Add or update endpoint tests for every API contract change.

## Backend API Contracts Definition

### Current API stack

The backend uses:

- Django REST Framework
- `dj-rest-auth`
- `django-allauth`
- `rest_framework_simplejwt.token_blacklist`
- JWT cookies through `dj_rest_auth.jwt_auth.JWTCookieAuthentication`
- CSRF cookie endpoint
- scoped throttling

### Current endpoints

From `authentication/urls.py`:

```python
router = DefaultRouter()
router.register("auth/csrf", CsrfCookieViewSet, basename="csrf")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", LoginView.as_view()),
    path("auth/social/google/", GoogleLoginView.as_view()),
    path("auth/registration/", RegisterView.as_view()),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
]
```

The project includes these routes under `/api/` from `config/urls.py`.

### Auth response rules

Current login/register/social login behavior:

- Set JWT access/refresh cookies.
- Remove raw `access` and `refresh` tokens from `response.data`.
- Flush session data.
- Remove session cookie.
- Remove messages cookie.
- Return user data including `completed_onboarding`.

Rules:

- Do not expose raw JWT tokens to the frontend.
- Keep auth responses JSON-only.
- Keep auth state in HTTP-only cookies.
- Keep `completed_onboarding` in user details unless the product contract changes.

### CSRF rules

Current CSRF endpoint:

```python
class CsrfCookieViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    throttle_scope = "auth_csrf"

    @method_decorator(ensure_csrf_cookie)
    def list(self, request: Request) -> Response:
        return Response({"csrfToken": get_token(request)}, status=status.HTTP_200_OK)
```

Rules:

- Unsafe auth requests must require CSRF.
- Frontend must fetch CSRF before login/register/logout when needed.
- Tests must use `APIClient(enforce_csrf_checks=True)` for CSRF contracts.

### Throttling rules

Current throttle scopes:

```python
"auth_csrf": "60/min"
"auth_login": "5/min"
"auth_registration": "5/min"
"auth_social_google": "10/min"
"dj_rest_auth": "10/min"
```

Rules:

- New auth-sensitive endpoints must have a throttle scope.
- Tests must prove throttling behavior for auth-sensitive endpoints.
- Do not remove throttling to fix tests.

### User serializer contract

Current `UserDetailsSerializer` exposes:

```text
id
email
first_name
last_name
profile_photo
completed_onboarding
```

Rules:

- Keep user response fields explicit.
- Do not expose password hashes, secrets, raw tokens, internal permissions, or provider secrets.
- Add tests for any field added or removed.

### Email identity rules

Current user identity behavior:

- `email` is the username field.
- Emails are normalized by stripping whitespace and lowercasing.
- Case-insensitive uniqueness is enforced at the database level with `Lower("email")`.
- Duplicate manual/social email registration is rejected.

Rules:

- Preserve case-insensitive email uniqueness.
- Validate duplicate emails at the API boundary and database boundary.
- Test case variants.

### Security settings contract

Current security behavior is controlled by `DEBUG`:

- Secure cookies are enabled when not debugging.
- SSL redirect and HSTS are enabled when not debugging.
- `SECURE_CONTENT_TYPE_NOSNIFF = True`.
- `SECURE_REFERRER_POLICY = "same-origin"`.
- `X_FRAME_OPTIONS = "DENY"`.

Rules:

- Do not weaken security defaults without an explicit task.
- Add settings tests for security-sensitive changes.
