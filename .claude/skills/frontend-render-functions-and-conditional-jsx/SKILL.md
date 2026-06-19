---
name: frontend-render-functions-and-conditional-jsx
description: Use when editing any front end component to prevent inline conditional JSX and require explicit render functions or extracted components.
---

# Frontend Render Functions and Conditional JSX

Use this skill when editing any frontend component, UI component, form element, page component, modal, side peek, table, card, or layout component.

## Core rule

Do not write inline conditional JSX inside the returned JSX tree.

Components must not render conditional elements with inline `&&` expressions or ternary expressions.

Conditional rendering must be handled through a named render function or an extracted component.

The render function must return the default result first.

## Forbidden inline conditional JSX

Do not write JSX like this:

- `{hasError && (...)}`
- `{isOpen && (...)}`
- `{items.length > 0 && (...)}`
- `{condition ? (...) : null}`
- `{condition ? (...) : (...)}`
- `{condition ? valueA : valueB}` inside JSX when it controls rendered markup
- nested ternaries inside JSX
- chained conditional JSX inside JSX

Inline conditional rendering is not allowed anywhere inside component markup.

## Required render function pattern

Use a named render function inside the component body.

The render function must check the default or empty state first.

Example structure:

- `const renderError = () => {`
- `if (!hasError) { return null; }`
- `return error element;`
- `};`

Then the JSX should call:

- `{renderError()}`

Do not inline the condition directly in the JSX.

## Default-first rule

Render functions must return the default state first.

For absent optional content, the default is usually `null`.

For empty lists, the default may be an empty state component.

For disabled or unavailable UI, the default may be the base/default component state.

Always structure render functions like:

- check missing, false, empty, or default state first
- return the default result
- return the rendered element after the guard

Do not invert this pattern.

## Error rendering

Do not render form errors inline with conditional JSX.

Do not duplicate error markup across Input, Select, textarea, checkbox, radio, or other form components.

Form validation errors must be abstracted into a shared UI component.

Expected shared component:

- `ui/form-elements/form-error`

The shared form error component must have its own props interface in the correct type file.

The shared form error component must be used by Input, Select, and any other form element that can show a field-level validation error.

## Alert usage

If the error is a field-level validation error, use the shared form error component.

If the error is a step-level, form-level, page-level, or API/server alert, use the existing shared alert component if one exists.

Do not create custom alert markup when a shared alert component already exists.

Do not duplicate alert styles inline inside form steps.

## Accessibility requirements

Conditional error and alert rendering must remain accessible.

Field-level error components must support:

- `id`
- error message text
- screen reader readable text
- connection through `aria-describedby`
- use by Input, Select, and other form fields

Fields with errors must set `aria-invalid`.

Fields with error text must include the error id in `aria-describedby`.

Step-level and form-level alerts must use the correct shared alert semantics.

## Component scope

Render functions must follow the frontend component scope rules.

Do not define render functions outside the component body.

Do not define helper functions above the component.

If the render logic is shared, extract it to a real shared component under the correct UI folder.

If the render logic belongs only to the component, keep the render function inside the component body.

## Extraction rule

Extract conditional markup into a component when:

- the same conditional UI appears in more than one component
- the conditional UI is a form error
- the conditional UI is an alert
- the markup has accessibility behavior
- the markup has reusable styling
- the render function becomes large or noisy

Keep component-specific conditional rendering as an internal render function only when it is not reusable.

## JSX readability

Returned JSX should be easy to scan.

The JSX tree should contain component calls and render function calls, not inline branching logic.

Good JSX shape:

- static markup
- shared components
- `{renderSomething()}`
- `{items.map(...)}` only when rendering lists that do not require inline conditional branches

Bad JSX shape:

- inline `&&`
- inline ternaries
- nested conditional branches
- repeated conditional markup
- duplicated error or alert elements

## Rule summary

Never use inline conditional JSX.

Use default-first render functions for component-specific conditional rendering.

Extract reusable conditional UI into shared components.

Use shared form error components for field errors.

Use shared alert components for form-level, step-level, page-level, or API/server alerts.

Keep all render functions inside the component unless the logic is extracted to a proper shared component.
