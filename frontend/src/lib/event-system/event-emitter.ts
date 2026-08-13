import EventEmitterDefinition, {
  EventListener,
} from './definitions/event-emitter-definition';
import { EventMapDefinition } from './definitions/event-map-definition';

type EventListeners<EventMap extends EventMapDefinition> = {
  [EventType in keyof EventMap]?: Set<
    EventListener<EventMap[EventType] & object>
  >;
};

export default class EventEmitter<
  EventMap extends EventMapDefinition,
> implements EventEmitterDefinition<EventMap> {
  private readonly listeners: EventListeners<EventMap> = {};

  on<EventType extends keyof EventMap>(
    event_type: EventType,
    listener: EventListener<EventMap[EventType] & object>
  ): void {
    const eventListeners = this.listeners[event_type] ?? new Set();
    eventListeners.add(listener);
    this.listeners[event_type] = eventListeners;
  }

  off<EventType extends keyof EventMap>(
    event_type: EventType,
    listener: EventListener<EventMap[EventType] & object>
  ): void {
    this.listeners[event_type]?.delete(listener);
  }

  emit<EventType extends keyof EventMap>(
    event_type: EventType,
    payload: EventMap[EventType] & object
  ): void {
    const eventListeners = this.listeners[event_type];

    if (eventListeners === undefined) {
      return;
    }

    for (const listener of eventListeners) {
      listener(payload);
    }
  }
}
