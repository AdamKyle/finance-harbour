---
name: frontend-import-aliases
description: Use when adding or changing Finance Harbour frontend imports or source aliases.
---

# Frontend Import Aliases

- Finance Harbour frontend cross-module imports use source aliases.
- Do not use deep parent traversal such as `../../../ui/...`, `../../../../lib/...`, or equivalent when crossing a top-level `frontend/src` module.
- Relative imports are allowed only for files in the same local module/component subtree, such as `./types/...`, `./definitions/...`, or a closely colocated sibling.
- Canonical top-level aliases are `assets`, `components`, `configuration`, `layout`, `lib`, `pages`, `router`, `styles`, `ui`, and `util`.
- When an alias is added or changed, keep `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/eslint.config.js`, `AGENTS.md`, and both `frontend-architecture` skills synchronized.
- Do not create an alias for a one-off feature folder.
- Do not rewrite local same-module imports into aliases merely for churn.
- Audit every `.ts` and `.tsx` file under `frontend/src/` after alias changes.
- Final frontend source must not contain a relative parent traversal whose destination is another top-level aliased `src` module.
