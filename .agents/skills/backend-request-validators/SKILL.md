---
name: backend-request-validators
description: Use when backend request payloads need validation before a view, viewset, registration flow, or service mutates data.
---

# Backend Request Validators

Use this skill when adding or changing backend request validation for Django REST Framework views, viewsets, auth endpoints, onboarding endpoints, or service entry points.

## Core rule

Request payload validation belongs in request validator classes, not in response serializers and not scattered inside views.

Do not use a DRF `ModelSerializer` as the primary validator for a request object when the payload is a request contract.

Request validators should behave like Laravel request classes: the child request class declares the rules, and the shared engine performs the validation.

## Engine location

The shared request validator engine must live in:

- `core/request_validator_engine/engine.py`

Shared engine definitions must live under:

- `core/request_validator_engine/definitions/`

Do not duplicate validation engines in individual apps.

## Request validator location

App-specific request validators must live under:

- `<app_name>/views/request_validators/<view_or_action_name>_request.py`

Examples:

- `authentication/views/request_validators/profile_onboarding_partial_update_request.py`
- `authentication/views/request_validators/register_request.py`

Use the existing app import style.

Add `__init__.py` files when required by the package structure.

## Class naming

Request validator classes must be named for the request they validate.

Examples:

- `ProfileOnboardingPartialUpdateRequest`
- `RegisterRequest`

Do not name request validators like serializers.

Do not put `Serializer` in a request validator class name.

## Child request validator responsibility

Child request validators should declare rules and messages only.

They should not duplicate the engine.

They should not manually parse every field when the shared engine can validate the field through rules.

They may define custom validation methods only for domain-specific validation that cannot be expressed through the shared basic rules.

## Initial supported rules

The engine should support basic rules first.

Required initial rules:

- required
- nullable
- string
- integer
- boolean
- list
- dict
- email
- max_length
- min_length
- choices
- unique

Do not build a large framework beyond the current task.

Add only the rules needed now plus the small baseline set requested by the skill.

## Validation result

Request validators must expose validated data after successful validation.

Views and services should consume validated data, not raw `request.data`.

Invalid data must raise a DRF-compatible validation error with field-level errors.

Do not return partially validated data after failure.

## View and viewset usage

Views and viewsets that mutate data must validate request data before saving.

Expected flow:

- create request validator with `request.data`
- validate the request
- use validated data to mutate the model or call a service
- create a structure serializer or response object
- return the response

Do not mutate models before request validation passes.

## Serializer separation

Use request validators for input/request validation.

Use structure serializers for response/output shape.

Use DRF serializers only when required by third-party integration or an existing framework contract.

When a third-party serializer must remain, delegate custom request validation to the request validator engine instead of duplicating rule logic inside the serializer.

## Registration serializer compatibility

`dj-rest-auth` and `django-allauth` may require a serializer class for registration integration.

When that integration serializer must remain, keep the serializer as a wrapper and move custom request rules into the app request validator.

The serializer must not duplicate rules that belong in the request validator.

Preserve the third-party save and cleaned-data contract.

## Error rules

Request validation errors must be clear, field-specific, and safe to expose.

Do not expose internal model details, raw database exceptions, stack traces, or secrets.

Do not rely on database `IntegrityError` as the normal API validation response.

## Tests required

Request validators need tests for:

- valid data passes
- required fields fail when missing
- nullable fields accept null when allowed
- type rules reject invalid types
- max/min length rules reject invalid values
- choices reject unknown values
- unique rules reject duplicates

View/viewset tests must prove invalid request data does not mutate the database.

## Rule summary

Request validators validate input.

Structure serializers serialize output.

The shared engine lives in `core/request_validator_engine/engine.py`.

App request classes live in `<app_name>/views/request_validators/`.

Third-party serializers may remain only as wrappers when framework integration requires them.
