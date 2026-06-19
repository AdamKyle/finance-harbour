---
name: backend-readable-control-flow
description: Use when editing backend Python logic to keep functions small, avoid deep nesting, and replace large conditional chains with clear dispatch or extracted methods.
---

# Backend Readable Control Flow

Use this skill when editing backend Python logic in request validators, services, views, viewsets, managers, serializers, model methods, or tests.

## Core rule

Backend functions must be small, readable, and easy to reason about.

Do not create large functions with nested loops, nested conditionals, and long chains of rule handling.

Break large functions into smaller methods with one clear responsibility.

## Function size

A function should do one thing.

If a function validates multiple rule types, dispatches multiple branches, mutates several fields, and builds errors, split it.

Prefer small private methods with clear names over one large method that handles everything.

Private methods are allowed in production code when they make production logic clearer.

The no-helper-method rule applies to tests, not production code.

## Nesting

Avoid deep nesting.

Do not put large `if` chains inside loops when the branch logic can be extracted.

Use guard clauses and early returns.

Default or no-op cases should return first when possible.

## Rule dispatch

When behavior is selected by a rule name, status name, field name, or action name, prefer dispatch over long conditional chains.

Acceptable patterns include:

- dictionary dispatch from rule name to validator method
- Python `match` statements when they improve readability
- small extracted methods per rule
- explicit guard methods

Do not use a long chain of `if validation_rule == ...` branches when a dispatch map or extracted rule method would be clearer.

## Request validator engines

Request validator engines must not become giant nested conditional files.

Validation engines should separate:

- field presence handling
- nullable handling
- simple rule dispatch
- parameterized rule dispatch
- individual rule validation
- unique lookup behavior
- error message resolution

Each rule should have a focused method when the logic is more than a trivial one-liner.

## Loops

Loops should remain readable.

A loop may coordinate work, but it should not contain all business logic inline.

If a loop body becomes large, extract the body into a named method.

If a loop contains nested branching for several independent cases, extract those cases into named methods or dispatch.

## Conditionals

Use conditionals for simple control flow.

Do not use conditionals as a replacement for structure.

Avoid:

- long `if` chains
- nested `if` blocks inside nested loops
- repeated condition checks
- mixed validation and mutation in the same branch
- hard-to-scan boolean expressions

Prefer:

- early returns
- named predicate methods
- named validation methods
- dispatch dictionaries
- `match` statements when readable

## Error handling

Error handling should be direct and predictable.

Do not build errors in several unrelated branches when a focused method can return the error message.

Do not return ambiguous values from validation methods.

A validation method should clearly return either:

- no error
- a field-level error message
- a typed validation result

## Readability over cleverness

Do not replace readable code with clever one-liners.

Do not use dictionary dispatch if it makes the code harder to type safely or harder to debug.

Use the clearest structure for the task.

## Rule summary

Keep backend functions small.

Avoid deep nesting.

Avoid long conditional chains.

Use early returns, extracted methods, dispatch maps, or `match` when they improve readability.

Request validator engines must be composed of focused methods, not one giant validation function.
