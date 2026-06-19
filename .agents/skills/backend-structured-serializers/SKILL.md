---
name: backend-structured-serializers
description: Use when you have to create structured serializers.
---

# Structured Serializers Skill

Use this skill when adding backend response serializers that should return a small, explicit, performance-conscious API shape.

## Purpose

Structured serializers exist to keep API responses clean, fast, predictable, and minimal.

They should be used when an endpoint needs a specific response shape instead of returning a full Django model serializer payload.

## Rules

- Return only the fields required by the endpoint.
- Do not expose full model payloads by default.
- Do not expose sensitive financial values unless the endpoint explicitly needs them.
- Use request.user ownership before serialization.
- Prefer typed structures for read responses when the endpoint returns composed or optimized data.
- Keep write validation serializers separate from response serializers.
- Do not mix business logic into serializers.
- Keep serializer files small and endpoint-specific when the response contract is specific.
- Serializer output should be easy to understand from the structure definition alone.
- All money fields must be returned as integer cents.

## Folder direction

Use this structure when structured serializers are needed:

- app_name/structures/
- app_name/structure_serializers/

Example file direction:

- debt_profile/structures/debt_profile_progress_structure.py
- debt_profile/structure_serializers/debt_profile_progress_serializer.py

## Response contract direction

Every structured serializer must make these obvious:

- input object or queryset
- output fields
- nested structures
- nullable fields
- money fields in cents
- whether a field is user-entered or generated

## Money fields

All money values must be serialized as integer cents.

Correct field naming:

- income_per_pay_period_cents
- current_balance_cents
- minimum_payment_cents
- current_payment_cents
- rent_or_mortgage_cents
- extra_payment_cents

Incorrect field naming:

- income
- balance
- minimum_payment
- amount
- dollar_value

## Validation

For write endpoints, validate required fields before saving.

For read endpoints, serialize only already-owned data.

Do not trust user_id from request data.

Use request.user as the source of truth.

## Onboarding response expectations

Onboarding progress responses should return only:

- current_step
- completed_steps
- form_data
- is_complete

Profile onboarding responses should return only:

- nickname
- profile_photo

Debt profile responses should return only the fields needed by the onboarding wizard.

## Tests

Every API response contract change needs backend tests proving:

- only expected fields are returned
- money values are cents
- anonymous users are rejected
- cross-user access is rejected
- invalid payloads are rejected
- sensitive fields are not returned
