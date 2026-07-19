---
name: frontend-behavioral-validation
description: Use after frontend behavior changes to validate Finance Harbour with the checks and evidence the repository actually supports, without inventing a test framework.
---

# Frontend Behavioral Validation

Use this skill after changing frontend behavior, forms, navigation, API hooks, validation, or reusable UI.

## Current repository fact

The current frontend has no committed frontend test files and no Jest, Vitest, React Testing Library, Playwright, or Cypress dependency in `frontend/package.json`.

Do not claim frontend automated tests were added or run when no test framework exists.

Do not add a test framework or testing dependencies unless the user explicitly requests dependency and test-infrastructure changes.

## Required current validation

Use the project command rules and run the narrowest existing checks permitted by the task.

The current comprehensive frontend command is:

```bash
docker compose run --rm --no-deps frontend yarn check
```

When the running container is required by the task, the equivalent existing-container command is:

```bash
docker compose exec -T frontend yarn check
```

The check currently covers:

- Prettier format checking
- ESLint with zero warnings
- strict TypeScript checking
- the configured unused-file command
- Vite production build

Do not describe these checks as behavioral tests.

## Behavior verification without an automated test framework

For behavior changes, provide deterministic manual verification steps based on the changed code.

Each verification step must include:

- starting route or screen
- required authentication/onboarding state
- exact user action
- expected visible result
- expected disabled/loading/error state when applicable
- expected navigation or API result
- regression check for the existing behavior being preserved

Do not write vague steps such as "test the page" or "make sure it works."

## API-hook verification

When an API hook changes, verify against the hook's actual contract:

- request URL comes from the existing enum
- request and response types come from existing `definitions/**`
- the shared `ApiHandler` is used
- credentials and CSRF handling remain centralized
- loading is set and reset correctly
- `AxiosError` handling follows the existing hook style
- the component consumes the hook rather than issuing Axios requests directly

## Form verification

When a form changes, verify:

- existing shared form elements are still used
- labels and error relationships remain accessible
- invalid data does not advance or submit
- loading prevents duplicate submissions where the current flow does so
- server errors remain visible
- valid data maps through existing request mappers before the API hook
- money remains converted using the existing cents/basis-points utilities

## Adding frontend tests later

When the user explicitly asks to introduce frontend tests:

1. Inspect the current package scripts and lockfile.
2. Treat the framework choice as a dependency/infrastructure change.
3. Do not pretend the repository already has a preferred test framework.
4. Add the smallest coherent setup.
5. Add commands to `package.json` and Docker-compatible hooks only when explicitly in scope.
6. Test behavior through public component output and user interactions rather than implementation details.

Until that explicit change occurs, use the current checks plus precise manual verification evidence.
