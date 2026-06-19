---
name: frontend-utility
description: Use when adding or changing frontend utility functions, money helpers, percentage helpers, mappers, parsers, formatters, or reusable feature helpers.
---

# Frontend Utility Rule

Use this rule when adding or changing frontend utility functions, money helpers, percentage helpers, mappers, parsers, formatters, or reusable feature helpers.

## Purpose

Frontend utilities must be typed, documented, reusable, and easy to understand.

Page components must not contain reusable utility logic.

## Utility placement

Feature-only utilities live inside the feature folder.

Example:

- components/pages/onboarding/utils/

Shared utilities live under lib only when reused across multiple features.

Example:

- lib/money/
- lib/dates/
- lib/formatting/

Do not place feature-only utilities in lib.

## Utility naming

Utility function names must describe what they do.

Good names:

- dollarsToCents
- centsToDollars
- percentageToBasisPoints
- validateDollarInput
- validatePositiveDollarInput
- validateInterestRateInput
- buildOnboardingFormData
- hydrateOnboardingFormData

Bad names:

- parse
- convert
- handle
- process
- check
- makeData

## Variable naming

Use clear, descriptive variable names.

Do not use single-letter variable names.

Avoid unclear names such as:

- n
- r
- d
- e
- val
- idx
- raw
- obj
- item
- temp

Use descriptive names such as:

- parsedAmount
- parsedPercentage
- submittedValue
- normalizedValue
- validationResult
- convertedCents
- basisPoints

## JSDoc requirements

Every exported utility function must have a valid JSDoc block.

Each JSDoc block must include:

- descriptive title
- short explanation of what it does and why
- params
- return
- throws when applicable

If the function does not throw, state that it does not throw.

Do not write useless comments that only repeat the function name.

## Money utility rules

Money conversion must not live in page components.

Use named utility functions.

Required examples:

- dollarsToCents
- centsToDollars
- validateDollarInput
- validatePositiveDollarInput

Do not use parseFloat directly in page components for money conversion.

Do not use Number directly in page components for money conversion.

Do not silently convert invalid money input to zero.

## Percentage utility rules

Percentage conversion must not live in page components.

Use named utility functions.

Required examples:

- percentageToBasisPoints
- validateInterestRateInput

Users enter human percentage values.

Examples:

- 25 means 25 percent
- 0.25 means 0.25 percent
- .25 means 0.25 percent

If the API field is interest_rate_basis_points, convert:

- 25 to 2500
- 0.25 to 25
- .25 to 25

Do not make users type backend-shaped percentage values.

Do not require a leading zero before a decimal percentage.

## Validation implementation inside utilities

Do not use regex as the primary validation strategy for money or percentage input.

Prefer explicit parsing, normalization, and numeric checks.

Validation must accept normal user input.

Interest percentage validation must accept:

- 25
- 25.5
- 25.50
- 0.25
- .25

## Page component restrictions

Page components must not contain:

- money conversion logic
- percentage conversion logic
- reusable parsing logic
- reusable formatter logic
- reusable mapper logic
- parseFloat for money or percentages
- Number for money or percentages

Page components may:

- call utility functions
- pass utility results to API mappers
- render validation results

## Mapper utility rules

Mapping functions must live outside page components when the payload is not trivial.

Examples:

- mapDebtFormToApiPayload
- mapIncomeFormToApiPayload
- mapExpenseFormToApiPayload

Mapper functions must:

- use typed inputs
- use typed returns
- avoid mutating input
- avoid API calls
- avoid UI state updates

## Acceptance criteria

Frontend utility code follows this rule when:

- reusable helpers live in utils or lib
- feature-only helpers stay inside the feature folder
- exported utility functions have valid JSDoc blocks
- variables use descriptive names
- money and percentage conversion lives in utilities
- page components do not use parseFloat directly for money or percentages
- page components do not use Number directly for money or percentages
- interest conversion accepts 25, 0.25, and .25
- lint, type-check, and format check pass
