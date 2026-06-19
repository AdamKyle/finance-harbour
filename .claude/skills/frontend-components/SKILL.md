---
name: frontend-components
description: Use when adding or changing React components, UI primitives, component props, styles, accessibility, or page components in Finance Harbour.
---

# Frontend Components Skill

Use this skill for React components, UI primitives, props, component folders, styles, and accessibility.

## Non-negotiable rules

- Each reusable component must have its own prop interface file under `types/`.
- Keep reusable primitives in `ui/**`.
- Keep page-specific components in `components/pages/**`.
- Keep style helper files under component-local `styles/**` where the current UI pattern uses them.
- Use `clsx` for conditional class composition.
- Use semantic elements and accessible labels.
- Do not create giant components when smaller render helpers or child components fit the existing style.

## Frontend Components Definition

### Current component patterns

Observed reusable UI pattern:

```text
ui/buttons/
  button.tsx
  icon-button.tsx
  link-button.tsx
  enums/button-variant.ts
  styles/button/base-styles.ts
  styles/button/variant-styles.ts
  types/button-props.ts
```

Observed form component pattern:

```text
ui/form-elements/
  input.tsx
  types/input-props.ts
```

Observed page-specific pattern:

```text
components/pages/registration/registration.tsx
components/pages/onboarding/onboarding.tsx
```

### Component file rules

- Use kebab-case filenames.
- Use PascalCase component names.
- Default-export components where the current folder does so.
- Named-export provider components where the current folder does so.
- Put prop interfaces in `types/<component-name>-props.ts`.
- Put enums in `enums/**` when component behavior has named variants.
- Put style builders in `styles/**` when style logic is reused or variant-driven.

### Props naming rules

The current UI components use snake_case prop names such as:

```text
on_click
additional_css
aria_label
show_label
navigate_to_route
```

Rules:

- Preserve this prop naming style for local project components.
- Do not silently rename existing props to camelCase.
- For native DOM props, keep native names like `autoComplete`, `onChange`, `htmlFor`, and `aria-*` attributes.
- Provide default values in the component signature when the current pattern supports it.

### UI primitive rules

For reusable `ui/**` components:

- Keep the component focused and presentation-oriented.
- Do not call domain API hooks from UI primitives.
- Accept data and handlers through props.
- Keep variants enum-driven, like `ButtonVariant`.
- Keep base styles and variant styles separate when a component has variants.
- Use `ts-pattern` only where existing variant matching uses it.

### Page component rules

For page-specific components:

- Keep form state local unless it must be shared globally.
- Use custom hooks for API actions.
- Use render helper functions for conditional UI when it improves readability, as seen in `renderSubmitButton`.
- Guard submit handlers with early returns.
- Keep loading buttons accessible with `aria_label` and disabled states.

### Accessibility rules

Current components use:

- `aria-label` fallback in button components.
- `aria-describedby` for input errors.
- `aria-invalid` for invalid fields.
- `aria-required` for required fields.
- `aria-labelledby` for page sections.
- Empty `alt` plus `aria-hidden="true"` for decorative images.

Rules:

- Do not remove accessibility attributes.
- Add keyboard-safe interactions for clickable elements.
- Prefer real buttons and links over clickable divs.
- Every form input must have a visible label.
- Every error message must be connected to the input it describes.

### Tailwind/class rules

- Use Tailwind utility classes.
- Use `clsx` for conditional classes.
- Preserve dark-mode classes where matching components already include them.
- Keep repeated variant strings in style helper files.
- Do not introduce unrelated CSS frameworks.

### Component output rules

- Return `ReactNode` where the existing pattern explicitly does so.
- Let TypeScript infer return type when the surrounding file pattern does not require explicit return type.
- Avoid `React.FC` unless the repo adopts it later.
