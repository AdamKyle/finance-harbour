---
name: frontend-types
description: Use when adding or changing TypeScript interfaces, definitions, enums, request/response shapes, props, or strict typing in Finance Harbour.
---

# Frontend Types Skill

Use this skill for TypeScript definitions, interfaces, props, enums, API request/response shapes, and strict typing.

## Non-negotiable rules

- Use interfaces for object contracts unless the current file uses a type alias for a functional or utility type.
- Keep each component prop contract in its own `types/**` file.
- Keep API/request/response/hook contracts in `definitions/**` files.
- Do not use `any`.
- Do not weaken `tsconfig` strictness.
- Do not hide errors with broad `unknown as` casts.

## Frontend Types Definition

### Current TypeScript config

The frontend uses strict TypeScript:

```json
"strict": true,
"noImplicitAny": true,
"skipLibCheck": false,
"isolatedModules": true,
"noEmit": true
```

Rules:

- Do not lower strictness.
- Do not add implicit any.
- Prefer precise nullable types over optional behavior when state can intentionally be null.

### Interface/type file placement

Observed patterns:

```text
ui/buttons/types/button-props.ts
lib/authentication/api/hooks/definitions/login-request-definition.ts
lib/authentication/api/hooks/definitions/login-response-definition.ts
lib/authentication/definitions/authentication-context-definition.ts
lib/core/api/definitions/user-definition.ts
configuration/deffinitions/modular-container-definition.ts
```

Rules:

- Component props go under `types/`.
- API contracts and hook return/parameter contracts go under `definitions/`.
- Preserve existing folder spelling where already present. The configuration and service-container modules currently use `deffinitions/**`; do not create a parallel `definitions/**` folder beside them.
- Use `definitions/**` where the surrounding module already uses that spelling.
- Do not mix prop interfaces into component files unless the component is genuinely one-off and the repo pattern changes.

### Interface rules

Use interfaces for object shapes:

```ts
export default interface ButtonProps {
  label: string;
  variant: ButtonVariant;
}
```

Rules:

- Prefer `interface` for props, request bodies, responses, context values, and user/domain objects.
- Use `type` for utility aliases, unions, function aliases, and existing patterns such as `StateSetter`.
- Export default interfaces where the current module does so.
- Use named exports where the current module does so, such as `UserDefinition`.

### API shape rules

For backend API data:

- Match backend field names exactly.
- Keep snake_case fields from backend responses, such as `completed_onboarding`.
- Do not rename backend data to camelCase unless a mapping layer exists.
- Keep request and response definitions separate.
- Add explicit error definition files for structured API errors.

### Enum rules

Observed enums:

```text
ui/buttons/enums/button-variant.ts
lib/authentication/api/enums/authentication-api-urls.ts
react-router/enums/navigation-routes.ts
```

Rules:

- Use enums for fixed route names, API URL names, and visual variants.
- Keep enum files in `enums/**`.
- Do not hardcode strings in many components when an enum exists.

### React type imports

Current code uses both regular and type imports:

```ts
import React, { ChangeEvent, FormEvent, ReactNode, useState } from 'react';
import type ButtonProps from './types/button-props';
```

ESLint currently has `@typescript-eslint/consistent-type-imports` turned off.

Rules:

- Follow the surrounding file’s import style.
- Use `import type` where the existing file/module already uses it.
- Do not change large import style across the app without an explicit formatting task.

### Error typing rules

Current API hooks use `AxiosError` and store API error data as typed hook errors.

Rules:

- Narrow caught errors with `err instanceof AxiosError` before reading `response`.
- Store `null` when there is no error.
- Do not assume all caught errors are Axios errors.
