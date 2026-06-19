---
name: frontend-formatting
description: Use when changing frontend linting, formatting, import order, package scripts, TypeScript checks, Prettier, ESLint, or Yarn commands in Finance Harbour.
---

# Frontend Formatting Skill

Use this skill for frontend formatting, linting, import order, TypeScript checks, package scripts, and pre-commit/pre-push alignment.

## Required commands and command boundaries

Use the project command rules before running frontend commands.

Default frontend validation, when the user has not provided a narrower command, is:

```bash
cd frontend
yarn cleanup
yarn lint
yarn type-check
yarn unused-files-check
yarn build
```

Or full check:

```bash
cd frontend
yarn check
```

If the prompt gives one exact frontend command, run only that command.

Do not run package install/update/remove commands unless the user explicitly asks for dependency changes.

Do not run `yarn build:dev` unless that script exists in `frontend/package.json` or the user explicitly requires it for the current branch.

## Frontend Formatting Definition

### Current package scripts

From `frontend/package.json`:

```json
"cleanup": "prettier --write \"src/**/*.{ts,tsx,css}\" && eslint \"src/**/*.{ts,tsx}\" --fix --max-warnings=0",
"build": "vite build",
"lint": "eslint \"src/**/*.{ts,tsx}\" --max-warnings=0",
"lint:fix": "eslint \"src/**/*.{ts,tsx}\" --fix --max-warnings=0",
"format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
"format:check": "prettier --check \"src/**/*.{ts,tsx,css}\"",
"type-check": "tsc --noEmit",
"unused-files-check": "unimported || true",
"check": "yarn format:check && yarn lint && yarn type-check && yarn unused-files-check && yarn build"
```

Rules:

- Use Yarn 4.
- Keep `--max-warnings=0` lint behavior.
- Do not remove `type-check` or `build` from final validation.
- Remember `unused-files-check` currently allows failure with `|| true`.

### Prettier rules

From `.prettierrc`:

```json
{
  "singleQuote": true,
  "trailingComma": "es5",
  "semi": true,
  "tabWidth": 2,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

Rules:

- Use single quotes.
- Use semicolons.
- Use 2-space indentation.
- Keep Tailwind class sorting through the Prettier plugin.
- Do not manually reorder classes against Prettier output.

### ESLint rules

Important current rules:

- `prettier/prettier`: error
- `@typescript-eslint/no-floating-promises`: error
- `@typescript-eslint/no-misused-promises`: error
- `unused-imports/no-unused-imports`: error
- `react-hooks/rules-of-hooks`: error
- `react-hooks/exhaustive-deps`: error
- jsx-a11y rules for alt text, anchors, click events, static interactions
- `import/order` with aliases
- `@stylistic/max-len`: 100
- `curly`: all
- `eqeqeq`: always
- `no-console`: only `warn` and `error` allowed
- `no-else-return`: error
- `prefer-const`: error

Rules:

- Do not add disable comments unless absolutely necessary and local to the line/block.
- Do not disable `react-hooks/exhaustive-deps` to silence missing dependencies.
- Fix unused imports rather than ignoring them.
- Keep import order grouped and alphabetized.

### Import order rules

Groups:

1. Builtin/external.
2. Internal/parent/sibling/index.
3. Blank lines between groups.
4. Alphabetize case-insensitively.

Alias path groups include:

```text
configuration/**
lib/**
assets/**
components/**
layout/**
pages/**
router/**
styles/**
ui/**
```

Rules:

- Use `react` first when imported.
- Use configured aliases for cross-folder imports.
- Do not use long relative imports across major folders.

### TypeScript check rules

- Run `yarn type-check` after type changes.
- Keep `strict` and `noImplicitAny` enabled.
- Do not add `// @ts-ignore` or `// @ts-expect-error` unless the task explicitly requires a documented exception.

### Pre-commit/pre-push rules

Current root `.pre-commit-config.yaml` runs frontend cleanup on pre-commit and frontend check on pre-push through Docker:

```bash
docker compose run --rm --no-deps frontend yarn cleanup
docker compose run --rm --no-deps frontend yarn check
```

Rules:

- Keep package scripts compatible with these hooks.
- Do not change scripts without updating hooks if needed.
