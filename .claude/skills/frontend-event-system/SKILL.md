---
name: frontend-event-system
description: Use for cross-feature or application-level frontend events in Finance Harbour.
---

# Frontend Event System

- Use the existing `lib/event-system/**` implementation for cross-feature or application-level frontend events.
- Use typed emitter-name enums, typed event enums, and typed event maps.
- Put payload interfaces/types in definition/type files following repository convention.
- Producers and consumers use `useEventSystem()`.
- Consumers register listeners in an effect and remove the exact listener during cleanup.
- Use `fetchOrCreateEventEmitter` following the existing Authentication and Payday patterns.
- Do not create another event bus, use DOM `CustomEvent`, use `EventTarget` as an application event bus, or use browser-global event dispatching.
- Do not use events merely to avoid normal props for direct parent/child communication.
- Use events when independently owned application features need to communicate without coupling rendering or state ownership.
- Event names describe domain/application behavior rather than DOM interactions.
