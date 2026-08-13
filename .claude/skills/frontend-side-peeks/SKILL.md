---
name: frontend-side-peeks
description: Use when creating or changing Finance Harbour application Side Peeks.
---

# Frontend Side Peeks

- Side Peeks are a shared application-level overlay system.
- Generic visual shell belongs under `ui/side-peek/**`; generic stack/navigation mechanics belongs under `lib/side-peek/**`; Finance Harbour registrations belong under `configuration/side-peek/**`; feature content belongs with its owning feature.
- Mount one Side Peek host at the authorized application level. Pages do not manually render fixed right panels.
- Open Side Peeks through the typed Finance Harbour Side Peek navigation/event interface. Names and props are compile-time typed through the Finance Harbour registry.
- The stack supports push, replace top, pop, and close all. Pushing does not unmount entries below it, and underlying state survives.
- Only the top entry is interactive. Inactive entries consistently use `inert`, `aria-hidden`, and disabled pointer interaction.
- One backdrop belongs to the host. Escape and backdrop clicks close only the top dismissible entry.
- Capture and pass the exact triggering element explicitly. Never obtain the opener from `document.activeElement`.
- Closing restores focus to the exact connected opener. Nested closing returns focus into the underlying Side Peek; final closing returns focus to the application trigger.
- Focus the top panel when opened. Panels have dialog semantics, accessible titles, and explicitly labelled close actions. Underlying application content cannot receive keyboard focus while active.
- Desktop panels slide gently from the right. Mobile panels use full width. Reduced motion retains state changes with zero duration.
- A multi-step wizard stays inside one Side Peek. Stacking is for a genuinely secondary flow, not wizard steps.
- Do not manipulate `document.body`, create a second Screen Manager, or repurpose the existing Screen Manager. Side Peeks may reuse its proven concepts while remaining a separate overlay responsibility.
