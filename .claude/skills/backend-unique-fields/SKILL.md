---
name: backend-unique-fields
description: Use when adding or changing Django model fields that represent names, labels, slugs, identifiers, or user-facing identity values.
---

# Backend Unique Fields

Use this skill when editing Django models, migrations, request validators, serializers, managers, or tests that add or change name-like or identifier-like fields.

## Core rule

Any field that acts like a name, label, slug, public identifier, or user-facing identity must be unique at the correct scope unless the task explicitly says duplicates are allowed.

Do not add name-like fields without thinking about uniqueness.

## Fields that usually require uniqueness

Apply this rule to fields such as:

- `name`
- `title`
- `label`
- `slug`
- `email`
- `username`
- `nickname`
- `code`
- `key`
- public identifiers
- user-defined labels used to look records up later

## Uniqueness scope

Choose the correct uniqueness scope for the domain.

Use global uniqueness for values that identify a user or public resource across the whole system.

Examples:

- email
- username
- public nickname
- public slug

Use user-scoped uniqueness for user-owned records where different users may use the same name.

Examples:

- a user's debt label
- a user's budget category name
- a user's saved plan name

User-scoped uniqueness must include the owner field in the database constraint.

## Optional unique fields

Do not use `unique=True` on an optional string field that allows blank values unless only one blank value is intended.

For optional fields that default to an empty string, use a conditional database constraint so multiple blank values are allowed and non-empty values are unique.

For optional nullable fields, use a conditional database constraint so multiple null values are allowed when the domain permits that.

## Case-insensitive uniqueness

Use case-insensitive uniqueness when users would reasonably see two values as the same.

Examples:

- `TestNick`
- `testnick`
- `TESTNICK`

These should not be allowed as separate identity values when the field is user-facing identity.

Use database-level constraints for case-insensitive uniqueness when possible.

## Database constraint requirement

Serializer or request validation is not enough.

Uniqueness must be enforced at the database level when the database stores the field.

Use one of these based on the domain:

- `unique=True` for required globally unique fields
- `UniqueConstraint` for scoped uniqueness
- conditional `UniqueConstraint` for optional unique fields
- expression-based constraints such as `Lower(...)` for case-insensitive uniqueness

## Request validation requirement

When a request can set a unique field, validate duplicates at the request boundary so the API can return a clear validation error.

Do not rely only on an `IntegrityError` bubbling out of the database.

Still keep the database constraint.

## Migration requirement

Changing uniqueness requires a migration.

Agents may create migration files when model changes require them.

Agents may run the Docker `makemigrations` command for the owning app when allowed by the task.

Agents must not run migrations.

## Tests required

Add or update tests for unique fields.

Tests must cover:

- the field accepts a valid unique value
- duplicate non-empty values are rejected
- case variants are rejected when uniqueness is case-insensitive
- multiple blank or null values are allowed when the field is optional and the domain permits blanks/nulls
- the database constraint rejects duplicates, not only the request validator

Use `transaction.atomic()` around expected database `IntegrityError` cases.

## Exceptions

Only allow duplicate name-like fields when the task or domain explicitly requires duplicates.

If duplicates are allowed, the code or prompt should make that reason clear.

Do not silently skip uniqueness on name-like fields.

## Rule summary

Name-like fields are unique by default.

Choose global or scoped uniqueness intentionally.

Optional unique fields need conditional constraints.

Case-insensitive uniqueness is required for user-facing identity values.

Validate at the request boundary and enforce at the database boundary.
