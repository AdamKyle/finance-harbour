---
name: frontend-spacing
description: Use when editing any front end component to define how spacing should work in the app.
---

# Frontend Spacing Rule

Use this rule when writing or editing TypeScript, React, hooks, utilities, API hooks, and page components.

## Purpose

Frontend code must be visually readable. Passing Prettier is not enough.

Related operations should be grouped with blank lines between distinct steps.

Do not compress API calls, state updates, navigation, and returns into one dense block.

## General rule

Use a blank line between different responsibilities inside a function.

A function should read like a sequence of clear steps.

Good grouping examples:

- set loading state
- reset error state
- perform API call
- update local or global state
- navigate
- return result
- handle error
- clear loading state

Each group should be separated by a blank line when the function contains multiple responsibilities.

## Required spacing in async hooks

Inside async API hooks, use blank lines between:

- loading state changes
- error reset
- API request
- auth or global state updates
- navigation
- return statements
- catch error handling
- fallback return statements
- finally cleanup

Do not write dense blocks where these operations touch each other directly.

## Correct async hook layout

Expected structure:

- setLoading true
- blank line
- setError null
- blank line
- try block
- API call
- blank line
- state update
- blank line
- navigation
- blank line
- return true
- catch block
- error state update
- blank line
- return false
- finally block
- setLoading false

## Bad pattern

Avoid dense code where loading, error reset, API calls, state updates, navigation, and returns are stacked together without spacing.

## Good pattern

Use spacing so each responsibility is visually separated.

## Required spacing in validation functions

Validation functions must separate:

- initial error object setup
- field validation
- derived booleans
- error state updates
- return result

Do not stack all validation logic without visual grouping.

## Required spacing in mapper functions

Mapper functions must separate:

- input cleanup
- conversion
- payload construction
- return

Do not mix filtering, conversion, and return construction into one dense expression when readability suffers.

## Required spacing in React components

Inside components, group code in this order with blank lines between groups:

- hooks
- derived state
- handlers
- render helpers
- return

Do not interleave handlers, state, and derived values randomly.

## Required spacing in imports

Keep the existing project import grouping style.

Use blank lines between:

- external packages
- relative imports
- lib imports
- components imports
- router imports
- ui imports

Do not collapse unrelated import groups.

## What Prettier does not decide

Prettier handles formatting.

This rule handles readability spacing.

If Prettier allows dense code but the code has multiple responsibilities touching each other, add blank lines manually.

## Do not overdo spacing

Do not add blank lines between every single line.

Only add blank lines between different responsibilities or logical steps.

## Acceptance criteria

Frontend code follows this rule when:

- async hooks have readable step spacing
- catch blocks separate error handling from fallback returns
- state updates are visually separated from API calls
- navigation is visually separated from state updates
- validation functions have grouped sections
- page components group hooks, derived values, handlers, and render logic
- imports keep existing project grouping
- Prettier, lint, and type-check still pass
