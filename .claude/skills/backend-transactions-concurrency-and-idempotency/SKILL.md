---
name: backend-transactions-concurrency-and-idempotency
description: Use when backend work changes multiple records, replaces collections, creates unique user state, handles retries, or may experience concurrent requests.
---

# Backend Transactions, Concurrency, and Idempotency

Use this skill for multi-record mutations, replacement operations, state transitions, unique record creation, and retry-sensitive endpoints.

## Current repository evidence

The current code uses:

- `transaction.atomic` for replacing required expenses
- `bulk_create` inside that transaction
- `get_or_create` for one-to-one user state
- database unique constraints for case-insensitive user identity and scoped required-expense sources
- `transaction.atomic()` in tests that expect `IntegrityError`

Preserve and extend these established patterns when the operation matches.

## Transaction boundary

Use `transaction.atomic` when one logical operation changes multiple rows or performs delete-then-create/replace behavior.

The transaction should wrap the complete consistency boundary, not only the final save.

Examples that require evaluation:

- deleting and recreating a selected collection
- updating a parent and dependent records together
- marking a workflow complete while updating related progress
- applying a payment-plan state transition across records

Do not wrap read-only code or unrelated work in a broad transaction without reason.

## Database invariants

- Use database constraints as the final boundary for uniqueness and relational invariants.
- Do not rely only on a pre-save `.exists()` check for concurrency-sensitive uniqueness.
- Keep request validation for clear client errors, but retain the database constraint.
- Handle expected `IntegrityError` only when the API needs to convert the race into an established validation response.
- Do not swallow an integrity failure and report success.

## `get_or_create` and `update_or_create`

Use `get_or_create` for the same one-record-per-owner pattern already present in the repository.

Before using it:

- confirm a database uniqueness constraint or one-to-one relation guarantees a single row
- scope the lookup by the authenticated owner
- provide explicit defaults when the model's defaults do not express the endpoint contract

Use `update_or_create` only when replacing the full supported state is the real operation. Do not use it to hide complex partial-update logic.

## Concurrent updates

Use `select_for_update` only when concurrent requests can cause a real lost update or invalid transition and the row is loaded inside `transaction.atomic`.

Do not add row locks speculatively.

When adding a lock, document:

- the row being locked
- the conflicting operations
- the invariant protected
- the transaction boundary
- the test that demonstrates the behavior or rollback

## Idempotency

Prefer natural idempotency from the current data model:

- one-to-one ownership
- unique constraints
- deterministic replacement of a selected collection
- focused updates of submitted fields

Do not create duplicate records on a retry when the endpoint represents setting current state.

Do not add an idempotency-key table, header, or middleware unless the task explicitly concerns retryable external operations and defines retention and ownership semantics.

## Side effects

Do not perform irreversible external side effects inside a database transaction without an explicit design for failure and retry.

The current repository does not establish an outbox, job queue, or external payment workflow. Do not invent one in a feature patch.

## Tests

For affected behavior, test:

- successful complete mutation
- rollback after a failure in the logical operation
- uniqueness at the database boundary
- repeated identical state-setting requests do not create duplicates
- cross-user requests do not touch another user's records
- expected `IntegrityError` with `assertRaises` and `transaction.atomic`, not a test-level try/catch

Do not use broad try/catch blocks in tests. Assert the expected exception directly.

## Completion evidence

Report the exact transaction boundary, database invariant, retry behavior, and tests performed.

Do not claim concurrency safety when no database constraint, transaction, lock, or deterministic state model supports the claim.
