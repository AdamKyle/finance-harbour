---
name: backend-spacing
description: Use when editing backend Python code to keep readable spacing between imports, validation, persistence, branching, serialization, and return statements.
---

# Backend Spacing

Use this skill when editing backend Python files, including models, managers, serializers, request validators, views, viewsets, services, tests, settings, and URL files.

## Core rule

Backend code must be easy to scan.

Do not compress multiple logical steps together without spacing.

Separate setup, lookup, validation, branching, persistence, serialization, and returns with blank lines.

## Import spacing

Imports must be grouped in this order:

- standard library imports
- third-party imports
- local application imports

Use one blank line between import groups.

Use two blank lines between the final import and the first class or function.

Do not use wildcard imports.

Use absolute imports for app modules.

## Method body spacing

Inside methods, separate logical stages with one blank line.

Common stages include:

- reading request data
- loading or creating models
- creating request validators
- validating data
- preparing update fields
- mutating model state
- saving data
- creating read serializers or response structures
- returning the response

Do not stack these stages together without spacing.

## View and viewset spacing

View and viewset methods must keep request validation, persistence, read serialization, and response returns visually separate.

Preferred order:

- load or create owned model data
- blank line when moving to the next logical stage
- create request validator or write serializer
- validate request data
- read validated data
- blank line
- mutate model fields
- save model state
- blank line
- create read serializer or response object
- blank line
- return response

Do not place the final return directly against serializer creation when the method performed work above it.

## Helper method spacing

Helper methods that perform a lookup or create an object must leave a blank line before returning the object.

If a helper method has only a direct return and no prior work, a blank line before return is not required.

## Branch spacing

Use a blank line before meaningful branches when the branch starts a new logical step.

Use a blank line after a branch when the next line starts a new logical step.

For update logic, separate each independent field update branch with a blank line.

Do not stack multiple independent `if` blocks tightly together when each branch mutates state.

## Long call spacing

Split long calls across multiple lines when they contain several arguments or nested structures.

Keep default dictionaries readable.

Do not force a long `defaults` dictionary onto one line when it makes the view harder to read.

Prefer readable multi-line calls over dense single-line calls.

## Return spacing

Use a blank line before a return when the return follows:

- validation
- persistence
- branching
- object creation
- response preparation
- serializer creation

A direct one-line return is acceptable only for tiny functions with no prior logical work.

## Test spacing

Tests must separate arrange, act, and assert sections with blank lines when the test has more than one section.

Do not compress setup, request execution, refreshes, and assertions into one dense block.

Keep tests readable without comments when possible.

## Formatting command

Use the project Docker backend formatting command from the README when backend formatting is required:

- `docker compose exec backend ruff format .`

Then validate formatting with:

- `docker compose exec backend ruff format --check .`

## Rule summary

Group imports correctly.

Separate logical backend stages with blank lines.

Separate independent branches that mutate state.

Break long calls when readability requires it.

Keep views, viewsets, services, validators, serializers, and tests readable beyond Ruff compliance.
