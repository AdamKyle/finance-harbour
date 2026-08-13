---
name: frontend-browser-global-access
description: Use when frontend code interacts with browser or DOM capabilities.
---

# Frontend Browser Global Access

- Do not use the global `window` or `document` identifier anywhere in Finance Harbour frontend source.
- Do not evade this rule with `globalThis.window` or `globalThis.document`.
- Do not use `document.querySelector`, `document.body`, `document.activeElement`, global browser event dispatching, or application event handling installed on `window`.
- Use React refs and element-scoped APIs for DOM operations. Owned element calls such as `someRef.current?.focus()`, `scrollIntoView()`, and `someRef.current?.querySelectorAll(...)` are allowed.
- Legitimate non-DOM browser capabilities may use `globalThis`, following existing patterns for timers, storage, location, `getComputedStyle`, or other platform APIs, but never as a route to `window` or `document`.
- Use the Event System for application events and React handlers for element interactions.
- Reusable browser interaction behavior belongs in the existing utility-hook pattern when appropriate.
