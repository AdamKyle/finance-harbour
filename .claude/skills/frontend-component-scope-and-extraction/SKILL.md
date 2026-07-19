---
name: frontend-component-scope-and-extraction
description: Use when editing any front end component to ensure component files contain imports and the component only, with props, types, constants, and functions kept inside or extracted correctly.
---

# Frontend Component Scope and Extraction

Use this skill when editing any frontend component.

## Core rule

A component file must not define anything outside the component except imports and the default export.

Do not define interfaces, types, constants, arrays, objects, helper functions, mappers, formatters, or default values above the component.

The component file should start with imports, then define the component.

## Not allowed outside the component

Do not define these outside the component body:

- interfaces
- types
- const arrays
- const objects
- default values
- helper functions
- factory functions
- field lists
- option lists
- image lists
- mappers
- formatters
- validators
- event handlers
- derived state

## Props interfaces

Component props must not be defined inline in the component file.

For a component named ProfileStep, the props interface must be named ProfileStepProps.

The props interface must live in a dedicated type file, for example:

types/profile-step-props.ts

The component imports the props interface from the type file.

## Constants and option lists

Do not define static arrays outside the component.

Do not do this outside the component:

PROFILE_PHOTOS
DEFAULT_PHOTO_ID
EXPENSE_FIELDS

If the values only belong to the component, define them inside the component.

If the values are shared, extract them to the correct dedicated file.

## Build inside the component

Component-specific values should be built inside the component body.

This includes:

- avatar options
- selected option logic
- alternate option logic
- field-specific display lists
- small component-only defaults

The component should keep its local display logic close to the JSX unless the logic is reused or too large.

## Extract when it does not belong

If logic does not belong inside the component, extract it.

Use the correct destination:

- Props interfaces go in a types file.
- Shared form state types go in a types file.
- Shared validation logic goes in validations.
- Shared data transformation goes in utilities.
- Shared request/state behavior goes in hooks.
- Shared UI belongs in the UI folder.
- Shared API request handling belongs in the API hook.

Do not leave shared logic floating above the component.

## Functions

Never define functions outside the component body.

Component-only handlers must be inside the component.

Shared functions must be extracted to the correct utility, hook, or validation file.

Do not create standalone functions above the component as a shortcut.

## Component readability

Prefer explicit component structure over hidden static config.

For simple forms, build fields inline.

Do not hide fields behind arrays like EXPENSE_FIELDS unless there is a strong reason and the pattern is approved.

If the component is getting too large, first reuse an existing component or use a local render helper. Create a child component only when the task requires a distinct feature responsibility and no existing component represents it.

## Rule summary

Only imports may exist before the component.

Everything else must either:

- live inside the component, or
- be extracted to a proper dedicated file that follows the frontend structure rules.

Do not place interfaces, constants, functions, option lists, or field lists outside the component.


## Extraction evidence rule

Do not extract simply because code could be moved.

Extraction is justified only by one of these repository-supported conditions:

- an existing component or hook already owns the responsibility
- more than one real consumer needs the same behavior
- the extracted unit has a distinct feature responsibility explicitly required by the task

Do not create a generic shared component, hook, or utility for one speculative use. Use `frontend-component-reuse-and-composition` before extraction.
