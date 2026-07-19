---
name: backend-security-and-soc2-controls
description: Use for every backend or API change involving authentication, authorization, financial data, logging, errors, secrets, or security controls in Finance Harbour.
---

# Backend Security and SOC 2 Control Support

Use this skill for every backend change that reads, writes, exposes, or protects user or financial data.

## Compliance boundary

Application code can support controls relevant to a SOC 2 examination, but application code by itself does not establish SOC 2 compliance.

Do not claim that a code change makes Finance Harbour SOC 2 compliant.

Use the AICPA Trust Services Criteria as the organizational control context and OWASP ASVS as a technical verification baseline. Apply only controls relevant to the task and the actual architecture.

Official references:

- AICPA, 2017 Trust Services Criteria with revised points of focus (2022)
- OWASP Application Security Verification Standard (ASVS)

## Current security controls verified in the repository

The current code includes:

- JWT authentication stored in HTTP-only cookies through `dj-rest-auth`
- CSRF enforcement for cookie-authenticated unsafe requests
- secure-cookie, HTTPS redirect, HSTS, no-sniff, referrer-policy, and frame-denial settings when `DEBUG` is false
- separate environment-backed Django and JWT signing keys
- password validators including a 12-character minimum
- scoped throttling for authentication endpoints
- explicit `IsAuthenticated` declarations on domain endpoints
- explicit `AllowAny` on the CSRF endpoint
- user-owned records loaded and created through `request.user` or a relation derived from `request.user`
- explicit response serializers with allow-listed fields
- database uniqueness constraints for identity and scoped unique values
- backend tests for authentication, CSRF, cookies, throttling, settings, ownership, and response fields

Preserve these controls unless the task explicitly changes the security design.

## Authentication and session rules

- Keep JWT tokens in HTTP-only cookies.
- Do not return raw access or refresh tokens in response bodies.
- Keep `withCredentials` and CSRF handling centralized in the frontend `ApiHandler`.
- Do not add a second authentication mechanism without explicit architectural scope.
- Do not weaken cookie, CSRF, HSTS, TLS, or password settings to make a feature or test pass.
- Keep secrets and signing keys in environment variables with no production fallback.

## Authorization and ownership rules

The project does not currently define a global DRF default permission class. Therefore every new API view or viewset must explicitly declare `permission_classes`.

Rules:

- Use `IsAuthenticated` for user or financial data.
- Use `AllowAny` only for a deliberately public endpoint and document why it is public.
- Do not accept a user identifier from request data as the ownership source for a user-owned record.
- Resolve ownership from `request.user` and user-owned relationships.
- Filter reads, writes, deletes, and related-object lookups by the authenticated owner.
- Do not rely on `OwnershipMiddleware` as the only authorization control; it only evaluates routes that contain `user_id`.
- Fail closed when ownership cannot be proven.
- Add anonymous-user and cross-user tests for every new user-owned endpoint.

## Request validation and mass-assignment rules

- Pass `request.data` through the app's request-validator classes before mutation.
- Consume `validated_data`, not arbitrary raw request fields.
- Update only explicitly supported fields.
- Do not call `setattr` with unvalidated or user-controlled field names.
- Keep request validation in `views/request_validators/**` and response shape in `structure_serializers/**`.
- Enforce important invariants at both the request boundary and database boundary when applicable.

## Response minimization

- Use explicit serializer fields.
- Keep response serializers read-only when they are used only for output.
- Do not serialize an entire model automatically when only a subset is required.
- Do not echo request payloads back unless the API contract explicitly requires those fields.
- Do not expose passwords, hashes, tokens, provider secrets, internal permission state, stack traces, or unrelated user fields.
- Add exact response-field tests for security-sensitive endpoints.

## Sensitive data in this repository

Treat these existing data categories as sensitive application data:

- email and authentication data
- income and pay-period data
- debts, balances, interest rates, and payments
- monthly and required expenses
- payment-plan data
- onboarding form data and progress

Rules:

- Do not log full request or response bodies containing this data.
- Do not use `print`, `pprint`, `dd`, dump helpers, or ad hoc console output.
- Do not place real user data in fixtures, examples, screenshots, prompts, or generated artifacts.
- Use synthetic values in tests.
- Do not duplicate sensitive data into another model or JSON field without a concrete product requirement and lifecycle analysis.
- Preserve integer cents and basis points rather than introducing floating-point financial storage.

## Logging and audit evidence

The current repository does not contain a dedicated audit-event model or centralized application security logging service.

Do not invent scattered per-view audit logging and call it a complete audit trail.

For a task that requires auditability:

1. Define the exact event types, actor, target, outcome, timestamp, and correlation fields.
2. Define which fields must be omitted or redacted.
3. Place the implementation in a dedicated cross-cutting service or app.
4. Protect audit records from ordinary user mutation.
5. Add tests proving successful and denied security-relevant events are recorded without sensitive payloads.
6. State any operational retention, access-control, alerting, or tamper-resistance requirement that remains outside application code.

For ordinary feature work, do not add ad hoc payload logging.

## Error handling

- Return DRF validation errors for expected invalid requests.
- Do not expose exception messages from database, framework, OAuth provider, or internal code directly to users unless they are an established safe API contract.
- Do not catch broad exceptions merely to return success or suppress a failure.
- Do not log credentials, tokens, cookies, or financial payloads in exception handlers.
- Preserve the real failure for monitoring while returning a generic unexpected-error contract when one is explicitly implemented.

## Throttling and abuse controls

- Preserve existing authentication throttle scopes.
- Add a throttle scope to a new authentication-sensitive or abuse-prone public endpoint.
- Do not add throttling blindly to normal authenticated CRUD without evaluating the actual operation.
- Test throttle behavior when a scope is added or changed.

## Dependency and supply-chain changes

- Do not add, remove, or upgrade security or authentication packages unless explicitly requested.
- Inspect the lockfile and official package documentation before a security dependency change.
- Never disable a security feature because a dependency integration is inconvenient.
- Report dependency scanning, secret scanning, or static security analysis only when the corresponding tool actually exists and was run.

## Required security tests

For affected behavior, add or update tests for:

- unauthenticated access
- authenticated owner success
- authenticated non-owner denial or isolation
- exact response fields
- invalid and unexpected request fields
- CSRF when cookie-authenticated unsafe requests are involved
- cookie/token response behavior for auth changes
- throttling for auth-sensitive endpoint changes
- database constraints for security-relevant invariants
- rollback when a protected multi-write operation fails

Use real Django code paths and the test database. Do not use mocks to bypass app-owned security behavior.
