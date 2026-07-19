---
name: frontend-component-reuse-and-composition
description: Use before any frontend UI change to discover and compose Finance Harbour's existing components instead of inventing new primitives or duplicating markup.
---

# Frontend Component Reuse and Composition

Use this skill before changing any page, layout, navigation, form, onboarding step, or reusable UI component.

## Repository-grounded rule

Inspect the repository before writing JSX.

Do not invent a component, hook, abstraction, prop, style system, or interaction pattern from memory.

The implementation must be assembled from existing Finance Harbour components and patterns whenever they can represent the requested behavior.

A new generic UI component or visual primitive is forbidden unless the task explicitly requires one and the repository inspection proves that no existing primitive can satisfy the requirement through composition or a compatible extension.

## Mandatory discovery order

Before editing frontend code:

1. Read the target component and its local `types/`, `definitions/`, `styles/`, hooks, and sibling components.
2. Search `frontend/src/ui/**` for an existing primitive.
3. Search `frontend/src/components/**`, `frontend/src/pages/**`, and `frontend/src/layout/**` for an existing feature component or composition pattern.
4. Search all current usages of the likely component, including its props, variants, accessibility behavior, loading state, and responsive classes.
5. Search the API hooks, validation hooks, and utilities already used by the feature.
6. Only after this inspection, choose the smallest change that reuses the existing implementation.

Do not create a new component merely because its name sounds appropriate.

## Current reusable UI inventory

The current repository contains these shared components:

```text
ui/alerts/alert.tsx
ui/buttons/button.tsx
ui/buttons/icon-button.tsx
ui/buttons/link-button.tsx
ui/cards/card.tsx
ui/cards/card-with-image.tsx
ui/dark-mode-toggle/toggle-dark-mode.tsx
ui/form-elements/form-error.tsx
ui/form-elements/input.tsx
ui/form-elements/money-input.tsx
ui/form-elements/select.tsx
ui/form-wizard/form-wizard.tsx
ui/form-wizard/form-wizard-nav.tsx
ui/form-wizard/step.tsx
ui/hero-section/hero-section.tsx
ui/sections/section-with-title.tsx
```

This inventory is a description of the current code, not permission to create similarly named replacements.

Use the existing component and its existing props, variants, type files, and styles.

## Existing composition evidence

The current frontend already follows these patterns:

- Page and feature components import interactive controls from `ui/**`.
- Generic form fields are centralized in `ui/form-elements/**`. The current source also uses local semantic `<button>` elements for specialized feature interactions that the shared button APIs do not currently represent, including profile-menu control, avatar selection, and selectable expense cards.
- Login and registration compose `Card`, `Input`, `Button`, and `IconButton`.
- Onboarding steps compose `Input`, `MoneyInput`, `Select`, `Button`, and `Alert`.
- Route-level pages may be thin wrappers around larger components, such as `pages/protected/onboard.tsx` rendering the existing `Onboarding` component.

Preserve these patterns.

## No invented controls

Do not add raw interactive markup to page, layout, or feature components when an existing shared component covers the exact behavior. Do not invent a new shared component merely to wrap a specialized one-off semantic interaction.

Examples:

- Use `Button` for labeled actions.
- Use `IconButton` for icon-led actions and loading-button states already represented by that component.
- Use `LinkButton` for link-styled actions.
- Use `Input`, `MoneyInput`, or `Select` for their existing field types.
- Use `Alert` for existing alert/error presentation.
- Use `Card` or `CardWithImage` for existing card compositions.
- Use the existing form-wizard components for wizard navigation and steps.

Do not reproduce their Tailwind classes inline in another component.

The current code uses local semantic buttons when the interaction requires capabilities not exposed by the shared components, such as:

- a DOM ref and profile-menu trigger semantics
- `aria-pressed` selectable images or cards
- rich dynamic children instead of a text label
- feature-specific menu-item or card layout

For the same kind of specialized interaction, keep semantic HTML local and accessible rather than inventing a generic primitive. Document why the existing `Button` or `IconButton` contract was insufficient.

## Extending an existing component

An existing component may be extended only when all of these are true:

- The requested behavior belongs to that component's current responsibility.
- The extension does not break current call sites.
- The extension preserves accessibility and current defaults.
- The new prop or variant is needed by a concrete task, not a hypothetical future use.
- The change is smaller and clearer than creating a parallel component.

Before adding a new prop or variant, inspect every current usage.

Do not add multiple unrelated boolean props that turn one component into several unrelated components.

## Feature components and abstraction

Keep feature-specific layout and orchestration in the existing feature folder.

Do not promote feature-specific behavior into `ui/**` merely to reduce line count.

Do not extract a child component solely because a file is long.

Use this order:

1. Reuse an existing component.
2. Keep a small, single-use handler or render function inside the owning component.
3. Reuse an existing feature component.
4. Create a new feature-specific component only when the task explicitly requires a distinct responsibility that cannot be represented cleanly by existing code.

A new feature component must still compose existing `ui/**` primitives. It must not introduce a new visual language.

## No speculative abstraction

Do not create shared utilities, hooks, components, config arrays, or generic wrappers for a single hypothetical future use.

Extraction requires concrete evidence:

- more than one real consumer, or
- a clearly cross-cutting concern already represented by the repository, or
- a distinct responsibility that cannot remain readable in the owner.

When only one component needs the behavior, keep it local unless an existing repository pattern places that responsibility elsewhere.

## Required completion evidence

For every frontend implementation, report:

- the existing components and hooks inspected
- the existing components reused
- any existing component extended and why
- every new component, if any, with the exact repository evidence that made it necessary
- confirmation that no duplicate generic control or parallel primitive was introduced; justify any local semantic control that existing shared component contracts cannot represent

Do not claim reuse without naming the actual files used.
