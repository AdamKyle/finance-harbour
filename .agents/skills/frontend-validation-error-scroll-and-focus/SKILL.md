---
name: frontend-validation-error-scroll-and-focus
description: Use when editing front end forms or validation flows to ensure failed validation scrolls or focuses the user to the relevant error area.
---

# Frontend Validation Error Scroll and Focus

Use this skill when editing any frontend form, onboarding step, wizard, modal form, page form, validation flow, submit handler, next handler, save handler, or shared form container.

## Core rule

When frontend validation fails after the user clicks Next, Continue, Save, or Submit, move the user to the relevant error area.

The user must not stay at the bottom of a form with no visible indication of why the action failed.

## When this applies

Apply this rule when validation fails during user-triggered form progression.

Examples:

- Next
- Continue
- Save
- Submit
- Finish
- Create
- Update

Do not scroll or focus while the user is typing.

Do not scroll or focus on successful validation.

Do not add global scroll behavior.

## Scroll target

Scroll to the top of the current form or the first visible form-level error area.

Prefer a real React ref.

Do not use fragile query selectors unless the project already has an approved pattern.

The scroll target should be stable, local to the current form, and easy to understand.

## Focus behavior

Prefer focusing the form-level error alert or error summary when one exists.

The focus target must be accessible.

If focus is moved to an alert or summary, that element must be able to receive focus safely.

Do not move focus to decorative elements.

Do not trap focus.

Do not create confusing focus jumps.

## Error summaries and alerts

Form-level, step-level, page-level, or API/server validation errors should use an existing shared alert component when one exists.

Do not create custom alert markup inline when the project already has shared alert components.

Field-level errors should remain next to the field and use the shared form error component.

## Submit and next handler flow

The expected failed-validation flow is:

1. Read the current form request data.
2. Run frontend validation.
3. If validation fails, set validation errors.
4. Scroll or focus the user to the form-level error area.
5. Bail before submit or next-step progression.

Do not submit when frontend validation fails.

Do not move to the next step when frontend validation fails.

## Accessibility requirements

Validation error scrolling must not break accessibility.

The error area should communicate what happened.

The user should be able to continue with keyboard navigation.

Screen readers should be able to identify the error state.

If the error area receives focus, it must have meaningful text.

## Component scope

Scroll and focus functions must follow component scope rules.

Do not define helper functions outside the component.

If the behavior is shared across multiple forms, extract it to a proper hook or shared component.

If the behavior belongs only to one component, keep it inside that component.

## Rule summary

When validation fails on form progression, scroll or focus the user to the form error area.

Use real refs when possible.

Use shared alert/error components.

Do not scroll while typing.

Do not scroll on successful validation.

Do not submit or continue when frontend validation fails.
