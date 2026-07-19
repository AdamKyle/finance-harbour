---
name: repository-grounded-change-completion
description: Use before finishing any Finance Harbour code task to prove the change follows inspected repository patterns and to prevent unsupported claims.
---

# Repository-Grounded Change Completion

Use this skill before presenting any completed Finance Harbour code change.

## Truthfulness rule

Every completion statement must be supported by one of:

- inspected repository code
- an actual diff
- an actual command result
- an actual test result
- an explicitly stated inference tied to inspected evidence

Do not say a requirement is complete, secure, performant, tested, or compliant without that evidence.

Do not fill missing context with a guessed convention.

## Required pre-change evidence

Before implementing, inspect:

- the target file
- its sibling files and local types/definitions
- existing call sites
- the closest analogous implementation
- relevant tests
- relevant skill files
- package/config files before choosing commands or dependencies

For frontend UI work, also inspect the existing `ui/**` inventory and usages.

For backend API work, also inspect permissions, ownership query paths, request validators, response serializers, model constraints, and tests.

## Frontend completion checklist

Confirm all applicable items:

- Existing components were searched before JSX was written.
- Existing `ui/**` primitives were reused.
- No duplicate generic form/action control was added outside `ui/**`; any local semantic control is justified by an interaction the existing shared component contracts cannot represent.
- No parallel generic component was invented.
- Any component extension preserves current call sites and accessibility.
- Page components use existing API hooks rather than direct Axios calls.
- Request/response types remain in existing definition files.
- Validation remains in the existing validation-hook/util pattern.
- Current Docker-compatible frontend checks were actually run, or the exact reason they were not run is stated.
- Manual behavior verification steps are provided when no automated frontend test framework exists.

## Backend completion checklist

Confirm all applicable items:

- The owning Django app and folder match current structure.
- User-owned data is tied to `settings.AUTH_USER_MODEL` or an owner-derived relation.
- Every API class explicitly declares permissions.
- Reads and writes are scoped through `request.user` or its owned relation.
- Request data passes through the existing request-validator boundary.
- Response fields are explicitly allow-listed.
- Sensitive data, secrets, tokens, and internal fields are not exposed or logged.
- Database constraints enforce invariants where required.
- Multi-record writes have a justified transaction boundary.
- Query access avoids repeated per-row queries and unbounded collections.
- Tests cover success, invalid input, anonymous access, cross-user isolation, and exact response fields where applicable.
- Actual backend checks/tests run are named exactly.

## New-file justification

List every new code file and state why an existing file or component could not fulfill that responsibility.

A new generic frontend component requires explicit task scope and repository evidence.

A new Django app requires a distinct domain responsibility.

A new dependency requires explicit user scope.

## Command reporting

Report only commands actually executed.

Separate:

- passed
- failed
- not run

Do not convert formatter, linter, type-check, build, or coverage output into a claim that behavior was manually verified.

Do not claim tests passed if the command was not run to completion.

## Security and compliance wording

Allowed wording:

- "preserves the repository's existing CSRF and cookie-auth controls"
- "adds tests for owner isolation"
- "supports the stated security control"

Disallowed wording without an independent audit:

- "SOC 2 compliant"
- "fully secure"
- "cannot be exploited"
- "production safe"

## Final evidence format

A completion report should identify:

1. inspected patterns
2. files changed
3. existing components/services reused
4. security, ownership, transaction, and query decisions
5. tests/checks actually run
6. anything not verified

Keep the report factual and scoped to the code reviewed.
