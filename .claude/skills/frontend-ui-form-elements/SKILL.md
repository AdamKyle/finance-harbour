---
name: frontend-ui-form-elements
description: Use when editing front end forms or creating reusable form controls to ensure form UI is abstracted into shared accessible UI components.
---

# Frontend UI Form Elements

Use this skill when editing any frontend form, onboarding step, settings form, filter form, modal form, side peek form, or reusable input/select control.

## Core rule

Form elements must be abstracted into shared UI components whenever possible.

Do not rebuild raw form fields inline inside page or step components when the field can be represented by a reusable UI component.

All shared form elements must live in the UI form elements folder.

## UI folder location

Shared form elements belong in the UI folder, following the same structure and naming style as the existing UI components.

Expected examples:

ui/form-elements/input
ui/form-elements/select

If a new form element is needed, create it in the UI form elements folder before using it across forms.

## Required shared form elements

The frontend must have shared generic components for:

- Input
- Select

Additional form elements should follow the same UI folder pattern when needed.

## Form element requirements

All shared form elements must be:

- Generic
- Screen reader friendly
- Mobile first
- Desktop second
- Fully accessible
- Clean
- Easy to reuse
- Easy to override when needed

## Styling rules

Shared form elements must use Tailwind.

Do not use calc unless explicitly instructed.

Do not use overflow-hidden unless explicitly instructed.

Do not create layout tricks that make the field harder to use on mobile or with screen readers.

## Defaults and overrides

Shared form elements should provide clean defaults.

Defaults may include:

- standard spacing
- label rendering
- error rendering
- help text rendering
- disabled state styling
- focus-visible styling
- mobile-first width behavior

Defaults must be overridable through props when a form needs a specific use case.

Do not make the component so specific that it only works for one onboarding step.

## Accessibility requirements

Every shared form element must support:

- label
- id
- name
- value
- disabled state when applicable
- error message when applicable
- aria-describedby when help text or errors are present
- aria-invalid when errors are present
- keyboard interaction
- visible focus state

Error text must be connected to the field for screen readers.

Labels must be real labels, not placeholder-only labels.

## Form component usage

Page-level and step-level components should compose shared UI form elements.

Do not write repeated raw input markup inline when the shared Input component can be used.

Do not write repeated raw select markup inline when the shared Select component can be used.

A form step should focus on:

- layout
- wiring values
- wiring field updates
- showing step-specific content
- calling the API hook request setter
- running validation when moving forward

A form step should not own reusable field markup that belongs in UI.

## Dynamic fields

Dynamic rows should still use shared UI form elements.

For example, a misc expense label field should use the shared Input component.

The dynamic row can be built in the step component, but the field itself must come from the shared UI form element.

## Do not create field definition arrays

Do not create field configuration arrays outside the component to generate form fields.

Avoid patterns like EXPENSE_FIELDS for simple step forms.

Build the form fields inline in the component so the form is readable and explicit.

If a form becomes too large, extract a real child component or hook instead of hiding the fields behind a static config array.

## When abstraction is required

Create or update a shared UI form element when:

- multiple forms need the same kind of field
- inline markup repeats across components
- accessibility behavior would otherwise be duplicated
- error handling needs consistent rendering
- label/help/error behavior should be standardized
- mobile-first behavior should be consistent

## Rule summary

Use shared UI form elements whenever possible.

Keep form elements generic, accessible, mobile-first, clean, and overridable.

Do not rebuild common inputs and selects inline across forms.

Do not use calc or overflow-hidden unless explicitly instructed.
