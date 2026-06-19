---
name: backend-formatting
description: Use when changing Python formatting, linting, imports, Ruff rules, pre-commit, or backend CI checks in Finance Harbour.
---

# Backend Formatting Skill

Use this skill for Ruff, formatting, imports, lint fixes, and backend CI/pre-commit consistency.

## Current backend formatter/linter

The backend uses Ruff from `backend/pyproject.toml`.

## Required commands and command boundaries

Use the project command rules before running backend formatting commands.

Default backend formatting validation is:

```bash
cd backend
ruff check .
ruff format --check .
```

Fix command, when formatting/lint fixes are required:

```bash
cd backend
ruff check . --fix
ruff format .
```

Do not run migration application commands while doing formatting work.

## Backend Formatting Definition

### Current Ruff config

From `backend/pyproject.toml`:

```toml
[tool.ruff]
target-version = "py314"
line-length = 120
exclude = [
    ".venv",
    "migrations",
]

[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "B",
    "UP",
    "DJ",
    "SIM",
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

### Python style rules

- Use double quotes.
- Use 4-space indentation.
- Keep line length at or below 120 unless a generated/third-party API shape makes that impractical.
- Keep imports sorted by Ruff.
- Use modern Python typing accepted by Python 3.14 target, such as `str | None`.
- Do not add per-line ignores unless the code has a real, documented reason.
- Do not change Ruff config to avoid fixing code.
- Do not format migrations manually; migrations are excluded.

### Import rules

Current backend imports follow this pattern:

```python
from typing import Any

from django.conf import settings
from rest_framework.response import Response

from authentication.models import User
```

Rules:

- Standard library imports first.
- Third-party imports second.
- Local app imports last.
- Use absolute imports for app modules.
- Do not use wildcard imports.

### CI/pre-commit parity

Current CI runs:

```bash
docker compose exec -T backend python manage.py check
docker compose exec -T backend ruff check .
docker compose exec -T backend ruff format --check .
```

Current pre-commit/pre-push uses Docker commands:

```bash
docker compose run --rm --no-deps backend ruff check . --fix
docker compose run --rm --no-deps backend ruff format .
docker compose run --rm --no-deps backend ruff check .
docker compose run --rm --no-deps backend ruff format . --check
```

Rules:

- Keep local commands and CI commands aligned.
- Do not add a second formatter for Python.
- Do not add formatting requirements that conflict with Ruff.

## Backend spacing rules

Backend formatting includes readable spacing, not only Ruff compliance.

Use the `backend-spacing` skill when editing backend Python code.

Separate logical stages with blank lines.

Do not stack validation, saving, read serialization, and return statements without spacing.

Break long function and constructor calls when readability requires it, even if they are under the Ruff max line length.

