---
name: backend-types
description: Use when you need to add types to the backend.
---

# Backend Types Skill

Use this skill when adding or changing backend utilities, services, serializers, validation helpers, model helper functions, or payment-plan logic.

## Purpose

Backend typing keeps the code easier to understand, safer to change, and clearer about whether a value is a model, id, string, integer, enum, list, or structured payload.

## Rules

- Add type hints to new Python functions.
- Type function arguments and return values.
- Avoid ambiguous names like data, obj, item, or thing when a clearer name exists.
- Use model instances when working inside request and response code.
- Use ids only for queued tasks or boundaries where model instances should not be passed.
- Do not use Any unless there is no better accurate type.
- Prefer explicit typed dictionaries, dataclasses, enums, or typed structures for known shapes.
- Keep enum values typed and centralized.
- Keep money values typed as int.
- Never use float for stored or calculated money values.

## Money types

All backend money values are integers in cents.

Examples:

- income_per_pay_period_cents: int
- current_balance_cents: int
- minimum_payment_cents: int
- current_payment_cents: int
- rent_or_mortgage_cents: int
- extra_payment_cents: int

## Function expectations

Good function shape:

- clear function name
- typed arguments
- typed return value
- no hidden mutation unless obvious from the function name
- no business logic inside serializers or viewsets if it belongs in a service/helper

Good examples:

- convert_dollars_to_cents(value: str) -> int
- create_payment_plan(debt_profile: DebtProfile) -> PaymentPlan
- validate_expense_payload(expenses: list[dict]) -> None
- get_owned_debt_profile(user: User) -> DebtProfile

Avoid:

- create_payment_plan(data)
- validate(obj)
- process(item)
- save_stuff(payload)

## User and model usage

Inside normal request code, prefer model instances.

Use:

- user=request.user
- debt_profile=debt_profile

Avoid:

- user_id=request.user.id
- debt_profile_id=debt_profile.id

Inside queued tasks, pass ids instead of model instances.

## Tests

Typed helper functions should have tests for:

- valid input
- invalid input
- zero values
- large values
- cent conversion boundaries
- ownership behavior where relevant
