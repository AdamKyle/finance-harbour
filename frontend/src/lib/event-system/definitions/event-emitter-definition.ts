import { EventMapDefinition } from './event-map-definition';

export type EventListener<Payload extends object> = (payload: Payload) => void;

export default interface EventEmitterDefinition<
  EventMap extends EventMapDefinition,
> {
  on<EventType extends keyof EventMap>(
    event_type: EventType,
    listener: EventListener<EventMap[EventType] & object>
  ): void;
  off<EventType extends keyof EventMap>(
    event_type: EventType,
    listener: EventListener<EventMap[EventType] & object>
  ): void;
  emit<EventType extends keyof EventMap>(
    event_type: EventType,
    payload: EventMap[EventType] & object
  ): void;
}
