---
name: frontend-architecture
description: Use when adding or changing React app structure, routing, layouts, providers, aliases, service container wiring, or frontend folders in Finance Harbour.
---

# Frontend Architecture Skill

Use this skill for frontend folder structure, routing, layouts, providers, aliases, and service wiring.

## Non-negotiable rules

- Keep source under `frontend/src/`.
- Use the existing aliases instead of deep relative imports when crossing folders.
- Keep reusable UI in `ui/**`.
- Search and compose existing `ui/**` and feature components before creating JSX or adding a component.
- Keep app/domain services and contexts in `lib/**`.
- Keep route declarations centralized through `finance-harbour-application.tsx` and `react-router/**` patterns.
- Keep page wrappers in `pages/**` and larger page-specific components in `components/pages/**`.
- Keep each component’s props in its own `types/**` interface file.
- Keep API request/response/hook contracts in `definitions/**` files. Preserve the existing `deffinitions/**` spelling in configuration and service-container modules unless a dedicated migration task renames it everywhere.

## Application layout rules

Use the project command rules before moving files, creating folders, or running commands.

The frontend application lives under `frontend/`.

All frontend source code lives under `frontend/src/`.

Do not create frontend source files outside `frontend/src/` unless the file is a root config file already used by the project.

Keep code in the current layout:

- `assets/**` for static frontend assets.
- `components/pages/**` for large page-specific components.
- `configuration/**` for dependency/container configuration.
- `layout/**` for shared layout pieces.
- `lib/**` for API, auth, service-container, and cross-cutting code.
- `pages/**` for route-level pages and wrappers.
- `react-router/**` for route enums, guards, and route utilities.
- `styles/**` for global styles.
- `ui/**` for reusable UI primitives.

## Frontend Architecture Definition

### Current frontend structure

Observed structure:

```text
frontend/src/
  app.tsx
  finance-harbour-application.tsx
  assets/
  components/
    authenticated-navigation/
    pages/
    public-navigation/
  configuration/
    deffinitions/
    modular-container.ts
  layout/
  lib/
    api-handler/
    authentication/
    core/
    service-container/
    service-container-provider/
    types/
  pages/
    protected/
    public/
  react-router/
    components/
    enums/
    public-routes/
    utils/
  styles/
  ui/
```

### App boot rules

`src/app.tsx` currently wraps the app with:

```tsx
<React.StrictMode>
  <BrowserRouter>
    <ServiceContainer>
      <ApiHandlerProvider>
        <AuthenticationProvider>
          <FinanceHarbourApplication />
        </AuthenticationProvider>
      </ApiHandlerProvider>
    </ServiceContainer>
  </BrowserRouter>
</React.StrictMode>
```

Rules:

- Do not bypass these providers.
- Add new global providers only here when they truly apply app-wide.
- Keep provider order intentional: routing, service container, API handler, authentication, application.

### Routing rules

`finance-harbour-application.tsx` owns route declarations.

Current route structure:

- Public layout wraps public pages.
- `OnboardingRedirectRoute` wraps public auth/landing routes.
- `ProtectedRoute` wraps authorized routes.
- `AuthorizedLayout` wraps protected pages.
- Paths come from `NavigationRoutes` enum.

Rules:

- Add route constants to `react-router/enums/navigation-routes.ts`.
- Use `Navigate`/`Outlet` wrapper components for route guards.
- Do not hardcode route strings throughout components.
- Use `navigateToRoute` utility where existing hooks accept navigation callbacks.

### Alias rules

The repo defines aliases in both `tsconfig.json` and `eslint.config.js`:

```text
assets/*
components/*
configuration/*
layout/*
lib/*
pages/*
router/*
styles/*
ui/*
util/*
```

Rules:

- Use aliases for cross-folder imports.
- Use relative imports for files inside the same local component/module folder.
- Keep alias config synchronized between TypeScript and ESLint.

### Page and component split

Use this separation:

- `pages/**`: route-level pages and wrappers.
- `components/pages/**`: larger page-specific components.
- `components/<feature>/**`: feature navigation/sections not generic enough for `ui`.
- `ui/**`: reusable primitives and shared visual building blocks.
- `lib/**`: API, auth, service container, cross-cutting hooks/context.

Do not put API hooks inside visual components. Do not put visual components inside `lib/**` unless they are provider/helper components for that lib module.

### Service container rules

The frontend uses `tsyringe`, `reflect-metadata`, and a service container.

Current pattern:

- `configuration/modular-container.ts` lists service containers.
- `lib/service-container/core-container.ts` registers modules.
- `lib/service-container-provider/service-container.tsx` boots the container.
- `lib/api-handler/axios-service-container.ts` registers API services.

Rules:

- Register cross-cutting services through modular containers.
- Add new service registration functions to `configuration/modular-container.ts`.
- Do not instantiate duplicate service singletons directly inside components.


## Repository-grounded composition gate

Use `frontend-component-reuse-and-composition` before any UI change.

The current source centralizes reusable interactive controls under `ui/**`. Preserve that architecture:

- do not add duplicate raw buttons, inputs, selects, or links in feature/page code
- do not invent a parallel visual primitive
- do not create a shared abstraction for a hypothetical future use
- use thin route wrappers when an existing feature component owns the screen
- extend an existing component only after inspecting every call site and only when the new behavior belongs to its current responsibility

Any new component must have a concrete task-defined responsibility and must compose the existing UI primitives.
