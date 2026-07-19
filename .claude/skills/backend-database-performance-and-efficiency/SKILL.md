---
name: backend-database-performance-and-efficiency
description: Use when changing Django queries, list endpoints, serializers, services, bulk writes, pagination, money calculations, or database indexes in Finance Harbour.
---

# Backend Database Performance and Efficiency

Use this skill for backend query design, collection endpoints, repeated mutations, serializers that traverse relations, and performance-sensitive services.

## Evidence-first rule

Do not add speculative caching, indexes, denormalization, query preloading, background work, or generic repository layers.

Inspect the actual queryset, related-object access, response serializer, model constraints, and tests before changing performance behavior.

Optimize a concrete query path, not an imagined future bottleneck.

## Current efficient patterns in the repository

The current code already uses these patterns:

- `get_or_create` for one-to-one user-owned records such as debt profile, monthly expense, payment plan, and onboarding progress
- `update_fields` for focused model updates
- `values_list(..., flat=True)` when only one related column is needed
- `bulk_create` for replacing selected required-expense rows
- `transaction.atomic` around the required-expense replacement
- bounded pagination with `per_page = 8` and a `data` plus `meta.pagination` response for important expenses
- integer cents and basis points instead of floating-point financial storage

Reuse these patterns where the same operation applies.

## Query ownership first

Performance must not weaken authorization.

- Start every user-owned query from `request.user` or a relation derived from it.
- Do not fetch a broad object and then check ownership in Python when the query can enforce ownership.
- Do not optimize by removing owner filters or permission checks.

## Avoid repeated queries

- Do not issue database queries inside loops when the required rows can be fetched once.
- Use `values_list` when only scalar values are needed.
- Use `select_related` for concrete foreign-key or one-to-one relations that are accessed for each row.
- Use `prefetch_related` for concrete reverse or many-valued relations that are accessed for each row.
- Do not add `select_related` or `prefetch_related` without checking the serializer and access path.
- Do not preload unrelated data.

## Writes

- Use `update_fields` when updating a known subset of model fields, matching the current view pattern.
- Use `bulk_create`, `bulk_update`, or a set-based queryset update only when model hooks/signals are not required and the behavior is tested.
- Keep multi-record replacement operations atomic.
- Do not call `save()` repeatedly in a loop when one supported set-based operation is clearer and equivalent.
- Do not use bulk operations if they would bypass required validation or invariant logic.

## Collection endpoints and pagination

- Bound any collection that can grow with user data.
- Reuse the existing paginated response shape when extending the important-expense/API-handler pagination contract:

```text
data
meta.can_load_more
meta.pagination.count
meta.pagination.current_page
meta.pagination.links
meta.pagination.per_page
meta.pagination.total
meta.pagination.total_pages
```

- Validate and normalize page inputs.
- Do not return an unbounded user-owned collection merely because the current dataset is small.
- Keep the frontend request contract aligned with `usePaginatedApiHandler` when that hook is used.

## Indexes and constraints

- Add a database index only for a demonstrated lookup, ordering, uniqueness, or join pattern.
- Prefer a uniqueness constraint when uniqueness is the invariant; do not substitute a non-unique index.
- Keep scoped uniqueness in the database, as with `debt_profile` plus `source_key`.
- Generate an app-scoped migration and inspect it.
- Do not run migrations.

## Money and calculation efficiency

- Store money as integer cents.
- Store percentage-like values as integer basis points where the existing model/API uses that contract.
- Do not introduce floating-point persistence for financial values.
- Keep conversion and validation at clear boundaries.
- Avoid recalculating unchanged derived values inside loops or repeated serializer property calls.

## Caching

The current repository does not establish an application cache layer.

Do not invent one for ordinary feature work.

Caching requires explicit scope covering:

- cache key ownership
- invalidation
- sensitive-data exposure
- expiration
- stale-data behavior
- tests

## Performance tests

Use tests when query shape or bounded behavior is part of the change:

- `assertNumQueries` for a concrete endpoint/service query budget
- pagination metadata and page-boundary tests
- tests proving bulk replacement produces the expected rows
- tests proving ownership filters remain intact
- tests proving no partial write occurs after failure

Do not assert an arbitrary query count without first measuring the current path and documenting what the count represents.

## Completion evidence

Report:

- the query path inspected
- the relations accessed
- any repeated query removed
- any bulk or focused update used
- any pagination/index change and its concrete reason
- tests or measurements actually performed

Do not claim a performance improvement without evidence from query count, reduced operations, or a directly simpler bounded path.
