---
name: backend-serializer-file-structure
description: Use when creating or editing backend serializers to ensure each serializer lives in its own file named after the serializer.
---

# Backend Serializer File Structure

Use this skill when editing backend serializers, structure serializers, nested serializers, request serializers, response serializers, or serializer imports.

## Core rule

Each serializer class must live in its own file.

Do not define multiple serializer classes in one file.

The file name must match the serializer class name in snake case.

## One serializer per file

Do not write serializer files like this:

- one file containing `MiscExpenseEntrySerializer`
- and `MonthlyExpenseWriteSerializer`
- and any other serializer class

Split them into separate files.

Correct structure:

- `misc_expense_entry_serializer.py`
- `monthly_expense_write_serializer.py`

Each file should contain one serializer class.

## Applies to all serializer folders

This rule applies to:

- `app_name/serializers/`
- `app_name/structure_serializers/`
- nested serializer folders
- write serializers
- read serializers
- response serializers
- third-party integration serializer wrappers

Do not make exceptions because a serializer is small.

## Naming

Serializer class names must use PascalCase.

Serializer file names must use snake_case.

Examples:

- `PaymentPlanWriteSerializer` lives in `payment_plan_write_serializer.py`
- `PaymentPlanSerializer` lives in `payment_plan_serializer.py`
- `MiscExpenseEntrySerializer` lives in `misc_expense_entry_serializer.py`
- `MonthlyExpenseWriteSerializer` lives in `monthly_expense_write_serializer.py`

## Imports

When a serializer depends on another serializer, import it from its own file.

Do not keep nested serializers in the same file just to avoid an import.

Use absolute app imports.

Do not use wildcard imports.

## Package exports

When the app already exports serializers through `__init__.py`, update the export.

Do not create duplicate exports.

Do not leave stale imports pointing at the old combined file.

## Serializer responsibility

Serializers should stay focused.

Write serializers validate write payloads only when the endpoint still uses DRF serializer validation.

Structure serializers define response shape.

Request validators validate request object contracts when the endpoint uses the request validator engine.

Do not mix request validation, response serialization, and business logic in one serializer file.

## Tests and references

When splitting serializers, update tests and references to import from the new file.

Do not change the API contract just because files were split.

Do not change serializer field names unless the task explicitly requires it.

## Rule summary

One serializer class per file.

File names must match serializer class names.

Split nested serializers into their own files.

Update imports and package exports.

Do not change behavior while splitting files.
