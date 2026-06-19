---
name: frontend-api-hooks
description: Use when changing frontend API handlers, axios service container, authentication hooks, contexts, CSRF handling, or service registration in Finance Harbour.
---

# Frontend API Request Structure Rule

Use this rule whenever adding or changing frontend API calls.

## Purpose

API calls must be organized, typed, predictable, and easy to locate.

Do not scatter API URLs, payload types, response types, or request logic inside page components.

Page components should call hooks. They should not know API route strings, Axios generics, request config details, or response parsing details.

## Folder structure

For a feature-specific API, the API folder lives inside the feature folder.

Example:

- components/pages/onboarding/api/
  - enums/
  - hooks/
    - definitions/
    - use-onboarding-progress.ts
    - use-save-profile-onboarding.ts
    - use-save-debt-profile.ts
    - use-save-monthly-expense.ts
    - use-complete-onboarding.ts

For a global/shared domain API, the API folder can live under lib.

Example:

- lib/authentication/api/
  - enums/
  - hooks/
    - definitions/
    - use-login.ts
    - use-register.ts
    - use-authenticated-user.ts

Do not put feature-only API hooks in lib unless the API is reused outside that feature.

## Required API folder layout

Every API folder must follow this structure:

- api/
  - enums/
    - feature-api-urls.ts
  - hooks/
    - definitions/
      - request-definition.ts
      - response-definition.ts
      - error-definition.ts when needed
      - use-feature-action-definition.ts
      - use-feature-action-params-definition.ts when needed
    - use-feature-action.ts

## API route enums

Every endpoint path must be defined in an enum file.

Do not hard-code API URLs inside hooks or components.

Correct:

- api/enums/onboarding-api-urls.ts

Example enum names:

- OnboardingApiUrls
- AuthenticationApiUrls

Enum values should be route paths only.

## API hooks

Every API call must have a dedicated hook.

Correct:

- use-onboarding-progress.ts
- use-save-profile-onboarding.ts
- use-save-debt-profile.ts
- use-save-monthly-expense.ts
- use-complete-onboarding.ts

Do not combine unrelated API calls into one generic hook.

Do not call apiHandler directly from page components.

Do not call Axios directly from page components.

## Hook definitions

Every API hook must have an explicit hook return definition.

Correct:

- definitions/use-onboarding-progress-definition.ts
- definitions/use-save-debt-profile-definition.ts

The hook definition must define:

- returned data
- loading state
- error state if exposed
- callable action signature
- action return shape

Example naming:

- UseOnboardingProgressDefinition
- UseSaveDebtProfileDefinition

## Request and response definitions

Every request payload must have a named request definition.

Every response payload must have a named response definition.

Correct:

- SaveDebtProfileRequestDefinition
- OnboardingProgressRequestDefinition
- OnboardingProgressResponseDefinition

Do not inline request/response object shapes inside hooks.

Do not use anonymous object types for API payloads unless the API truly has no payload.

Do not use any.

Avoid broad unknown-to-record parsing inside hooks. If parsing is needed, move it into a typed mapper or utility.

## API hook behavior

Hooks must:

- use the existing apiHandler pattern
- use route enums
- use named request/response definitions
- expose loading state
- expose readable errors where needed
- return explicit success/failure results for mutations that block user flow

Mutation hooks that affect wizard navigation must return:

- ok: true on success
- ok: false and error on failure

Do not swallow API errors when the calling UI needs to block progress.

## Utilities

Shared frontend utilities must live in an appropriate utils folder.

Feature-only utilities live inside the feature folder.

Example:

- components/pages/onboarding/utils/

Cross-feature utilities live under lib.

Example:

- lib/money/

Money utilities should not live inside page components.

Required money utility examples:

- dollarsToCents
- centsToDollars
- validateDollarInput

Percentage utilities should be separate from money utilities when behavior differs.

Required percentage utility examples:

- percentageToBasisPoints
- validatePercentageInput

Do not use parseFloat directly in page components for money or percentage conversions.

## Page component restrictions

Page components must not:

- define API URLs
- define API request payload interfaces
- define API response interfaces
- call apiHandler directly
- call Axios directly
- contain money conversion logic
- contain percentage conversion logic
- contain large API payload mapping logic

Page components may:

- call API hooks
- pass form state to a hook or mapper
- render loading/error state
- react to API hook results

## Import rules

Feature components should import feature API hooks from their own feature folder.

Correct:

- components/pages/onboarding/api/hooks/use-onboarding-progress

Avoid for feature-only APIs:

- lib/onboarding/api/hooks/use-onboarding-progress

Only use lib when the API is truly shared outside the feature.

## Acceptance criteria for API code

API work is acceptable only when:

- every endpoint path is in an enum
- every API call has a dedicated hook
- every hook has a return definition
- every request payload has a request definition
- every response payload has a response definition when response data is used
- page components do not call apiHandler directly
- page components do not define API payload types
- page components do not hard-code API URLs
- mutation hooks do not swallow blocking errors
- money and percentage conversion are in utilities, not page components

## Frontend API Hooks Definition

### Current API handler pattern

The app uses `lib/api-handler/api-handler.tsx` as the axios wrapper.

Current behavior:

- Adds `/api` prefix if missing.
- Sends `withCredentials = true`.
- Adds `Accept: application/json`.
- Adds `X-Requested-With: XMLHttpRequest`.
- Reads `csrftoken` from cookies.
- Sends `X-CSRFToken` when present.
- Returns `response.data`.

Rules:

- Do not bypass `ApiHandler` for normal backend calls.
- Do not duplicate CSRF/header logic in components.
- Do not expose raw response objects unless a task requires headers/status metadata.
- Keep generic request/response typing precise.

### Context/provider pattern

Observed context pattern:

```text
lib/api-handler/api-handler-context.ts
lib/api-handler/components/api-handler-provider.tsx
lib/api-handler/hooks/use-api-handler.ts
lib/authentication/authentication-context.ts
lib/authentication/components/authentication-provider.tsx
lib/authentication/hooks/use-authentication.ts
```

Custom context hooks must:

- Use `useContext`.
- Throw a clear error when used outside the provider.
- Return the typed context definition.

Provider components must:

- Accept children through a props interface file.
- Keep provider value explicit.
- Avoid unrelated side effects.

### Authentication hook pattern

Current auth hooks live under:

```text
lib/authentication/api/hooks/
  use-authenticated-user.ts
  use-csrf-token.ts
  use-google-social-auth.ts
  use-google-social-auth-callback.ts
  use-login.ts
  use-logout.ts
  use-register.ts
```

Each hook has colocated definitions for:

- request shape
- response shape
- error shape
- hook return shape
- hook params shape when needed

Rules:

- New API hooks must follow this structure.
- Keep hook state explicit: `error`, `loading`, and request/data state when needed.
- Use `useCallback` for async operations referenced by effects.
- Include all dependencies required by `react-hooks/exhaustive-deps`.
- Use early returns for empty request data.
- Do not swallow errors except where the current pattern intentionally catches an invoked async effect with `.catch(() => {})` after internal state is set.

### Auth flow rules

Current login/register hooks:

1. Fetch CSRF token.
2. Submit auth request through `apiHandler.post`.
3. Set authenticated user from the response.
4. Navigate to onboarding if `completed_onboarding` is false.
5. Navigate home otherwise.
6. Store structured Axios errors in hook state.

Rules:

- Preserve this flow unless auth/product behavior explicitly changes.
- Do not expect raw JWT tokens in the response body.
- Do not put auth tokens in browser storage.
- Keep navigation route constants from `NavigationRoutes`.

### Service container rules

Current service registration pattern:

```text
configuration/modular-container.ts
lib/service-container/core-container.ts
lib/service-container-provider/service-container.tsx
```

Rules:

- Register cross-cutting API/services through the modular container.
- Add service containers to `configuration/modular-container.ts`.
- Do not create parallel dependency systems.
- Keep `reflect-metadata` imported at app startup.

### API URL rules

API URL constants live in enum files such as:

```text
lib/authentication/api/enums/authentication-api-urls.ts
```

Rules:

- Add new endpoint constants to the relevant enum.
- Do not scatter literal API paths across components.
- Let `ApiHandler` add `/api` prefix.
