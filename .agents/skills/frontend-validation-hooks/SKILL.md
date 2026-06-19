---
name: frontend-validation-hooks
description: Use when adding or changing frontend form validation hooks, validation result definitions, field errors, or step validation logic.
---

# Frontend Form Validation Rule

Use this rule when adding or changing frontend form validation.

## Purpose

Frontend validation must be typed, reusable, predictable, and separated from page components.

Page components must not contain validation engines, validation error interfaces, or repeated field validation blocks.

## Validation folder structure

All feature form validation must live in a validations folder.

Use this structure:

- validations/
  - hooks/
    - definitions/
    - use-component-name-form-validation.ts

For onboarding, use:

- components/pages/onboarding/validations/hooks/use-onboarding-form-validation.ts
- components/pages/onboarding/validations/hooks/definitions/use-onboarding-form-validation-definition.ts
- components/pages/onboarding/validations/hooks/definitions/onboarding-validation-result-definition.ts
- components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition.ts

## Validation hook naming

Validation hooks must follow this naming pattern:

- use-component-name-form-validation

Examples:

- useOnboardingFormValidation
- useRegistrationFormValidation
- useDebtProfileFormValidation

## One validation hook per form

Each form should have one validation hook.

If a form wizard is one form split into multiple steps, use one validation hook for the wizard.

For onboarding, use one validation hook:

- useOnboardingFormValidation

That hook may expose step-specific validation functions:

- validateProfileStep
- validateDebtStep
- validateIncomeStep
- validateExpenseStep

## Validation hook rules

Validation hooks must:

- contain form validation logic
- return typed validation results
- expose named validation functions
- avoid API calls
- avoid backend state mutation
- avoid navigation
- avoid side effects outside validation

Validation hooks must not:

- call API hooks
- call apiHandler
- call Axios
- navigate
- save progress
- mutate server data
- contain UI rendering

## Validation definitions

Every validation hook must have explicit definition interfaces.

Do not inline validation return types inside the hook file.

Definitions must live in:

- validations/hooks/definitions/

Required definition examples:

- UseOnboardingFormValidationDefinition
- OnboardingValidationResultDefinition
- OnboardingFormErrorsDefinition
- DebtFieldErrorsDefinition
- IncomeFieldErrorsDefinition
- ExpenseFieldErrorsDefinition
- MiscExpenseFieldErrorsDefinition

## Validation result shape

Validation functions should return a consistent shape.

Use:

- is_valid
- step_error
- field_errors

Do not return only boolean values when the UI needs validation messages.

Do not make page components build validation errors manually.

## Page component restrictions

Page components must not contain:

- large validation functions
- validation error interfaces
- repeated field validation blocks
- money parsing validation
- percentage parsing validation
- regex validation logic
- single-letter validation loop variables

Page components may:

- call validation hooks
- store validation results in state
- pass validation errors to step components
- block submit or next actions based on validation results

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
- debtEntry
- debtIndex
- fieldErrors
- validationResult
- miscExpense
- onboardingProgress

## Validation behavior

Validation must produce clear user-facing messages.

Do not use vague messages like:

- Invalid
- Error
- Bad request

Use specific messages like:

- Enter an interest rate.
- Enter a valid amount.
- Amount cannot be negative.
- Enter a label, or remove this expense.

## Acceptance criteria

Frontend validation follows this rule when:

- validation logic lives in validation hooks
- validation hook definitions live in validations/hooks/definitions
- page components call validation hooks instead of owning validation logic
- validation functions return typed validation results
- validation messages are specific and user-friendly
- variables use descriptive names
- lint, type-check, and format check pass
