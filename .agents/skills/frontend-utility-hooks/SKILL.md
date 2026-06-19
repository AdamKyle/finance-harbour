---
name: frontend-utility-hooks
description: Use when creating or editing reusable frontend utility hooks so shared behavior is extracted into the proper utility hook folder with typed definitions.
---

# Frontend Utility Hooks

Use this skill when editing frontend code that creates, moves, or reuses shared hook behavior.

## Core rule

Reusable hook behavior must not live inline inside page, step, form, modal, side peek, or UI components.

If a hook-like behavior can be reused across more than one component, extract it to a utility hook.

Utility hooks must live under the frontend utility hook folder.

## Folder layout

Utility hooks must follow this structure:

- `util/hooks/use-hook-name.ts`
- `util/hooks/definitions/use-hook-name-definition.ts`

Use the existing project root and import aliases.

If the project already uses `utils` instead of `util`, follow the existing project folder name.

Do not invent a second utility folder.

Do not place utility hooks inside page folders unless the hook is page-specific and not reusable.

## Hook naming

Utility hooks must start with `use`.

Examples:

- `useScrollToTop`
- `useFocusElement`
- `useOutsideClick`
- `useDebouncedValue`

The filename must match the hook name in kebab case.

The exported hook name must match the file purpose.

## Definition files

Hook return types, config interfaces, and callback definitions must live in the hook definitions folder when they are not trivial.

Do not define reusable hook interfaces inline in the hook file.

Do not define hook interfaces inside consuming components.

Do not use casts to avoid creating proper definitions.

## Component usage

Components should call utility hooks and use the returned function or values.

Components must not duplicate reusable browser behavior inline.

For example, scroll-to-top behavior should be called from a hook such as `useScrollToTop`.

The component should not directly own reusable logic like:

- `window.requestAnimationFrame`
- `scrollIntoView`
- reusable focus behavior
- reusable browser event wiring
- reusable timeout cleanup
- reusable keyboard or pointer listeners

## Scope rule

If the behavior belongs only to one component and is not reusable, keep it inside the component as a named function.

If the behavior is reusable across the app, extract it to a utility hook.

Do not place reusable hook logic above the component.

Do not place reusable hook logic inside the component just because only one component uses it right now.

## Accessibility

Utility hooks that move scroll or focus must preserve accessibility.

A hook that scrolls or focuses should:

- accept a real React ref when possible
- avoid fragile query selectors
- support focus only when the element exists
- avoid focus traps
- avoid decorative focus targets
- not scroll on every render
- only run when explicitly called or when a clear dependency changes

## Browser APIs

Browser APIs must be referenced through `window` when required by project lint rules.

Examples:

- `window.requestAnimationFrame`
- `window.setTimeout`
- `window.clearTimeout`

Do not use browser globals directly if lint requires explicit `window`.

## Cleanup

Hooks that create listeners, timers, observers, or animation frames must clean them up.

Do not leak event listeners.

Do not leave pending timers or observers when a component unmounts.

## Rule summary

Reusable hook behavior belongs in `util/hooks`.

Hook definitions belong in `util/hooks/definitions`.

Components should call utility hooks instead of owning reusable browser behavior inline.

Scroll, focus, event, observer, and timing behavior must be accessible, typed, reusable, and cleaned up.
