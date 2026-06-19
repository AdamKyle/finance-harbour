---
name: frontend-type-safety-and-derived-values
description: Use when editing front end TypeScript, components, hooks, form elements, or accessibility wiring to prevent type casting/coercion and require readable derived values.
---

# Frontend Type Safety and Derived Values

Use this skill when editing any frontend TypeScript file, React component, UI component, form element, hook, validation file, API hook, page, modal, side peek, or layout component.

## Core rule

Do not coerce, cast, or force a value into the type you want.

The value must be correctly typed at the source.

If the code needs a boolean, the prop, state value, or derived value must already be a boolean.

Do not hide weak typing with casting, coercion, assertions, or truthy/falsy shortcuts.

## Forbidden casting and coercion

Do not use these patterns to force values into expected types:

- `Boolean(value)`
- `String(value)`
- `Number(value)`
- `value as SomeType`
- `value as boolean`
- `value as string`
- `value as number`
- `as unknown as SomeType`
- non-null assertions such as `value!`
- truthy/falsy coercion when a real boolean should exist

Do not replace one cast with another cast.

Fix the source type instead.

## Boolean values

Boolean values must be explicit.

Use properly typed boolean props and variables such as:

- `hasError: boolean`
- `isDisabled: boolean`
- `isSelected: boolean`
- `isLoading: boolean`
- `isOpen: boolean`

Do not pass a string, object, array, or nullable value and then cast it to a boolean inside the component.

Do not write `const hasError = Boolean(error)`.

If a component needs to know whether an error exists, pass `hasError` as a boolean or derive it through clear typed logic without coercion.

If a component also needs the error message, pass the error message separately as an optional string.

## Optional values

Optional values must be typed as optional.

Nullable values must be typed as nullable.

Do not cast optional or nullable values away.

Do not use non-null assertions to silence TypeScript.

Handle missing values with explicit guard clauses.

## Derived values must be readable

Do not build derived values with compact ternaries, chained truthy checks, or filter chains.

Avoid patterns like:

- inline ternaries
- nested ternaries
- `filter(Boolean)`
- array construction just to remove falsey values
- chained `.join(...) || undefined`
- hard-to-read one-line derived expressions

Use named functions with clear if statements and early returns.

## Accessibility derived values

Accessibility values must be obvious and readable.

Do not build `aria-describedby` with arrays, ternaries, `filter(Boolean)`, and `join`.

Use a named function.

The function must:

- live inside the component unless shared
- use explicit if statements
- return the default first
- return `undefined` when there is no description
- return the help text id when only help text exists
- return the error id when only error text exists
- return both ids when both exist
- not use ternaries
- not use `filter(Boolean)`
- not use type casts

## Function placement

Derived-value functions must follow component scope rules.

Do not define them outside the component body.

If the logic is shared, extract it to the correct utility or shared component.

If the logic belongs only to the component, keep it inside the component.

Do not place helper functions above the component.

## Allowed conversions

Only parse or convert values at real data boundaries.

Examples of valid boundaries:

- converting text input into a request value during validation
- preparing a backend request payload
- parsing a backend response when the backend contract requires it
- formatting display values from already-valid data

Do not use conversion as a replacement for correct TypeScript types.

Do not use conversion to silence type errors.

## Rule summary

Do not cast or coerce values to the type you want.

Fix the source type.

Use explicit boolean props.

Use readable named functions for derived values.

Do not use compact ternary, `filter(Boolean)`, or chained expressions for accessibility ids.
