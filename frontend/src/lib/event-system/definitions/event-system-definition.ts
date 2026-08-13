import EventEmitterDefinition from './event-emitter-definition';
import { EventMapDefinition } from './event-map-definition';

export default interface EventSystemDefinition {
  isEventRegistered(name: string): boolean;
  registerEvent(name: string): void;
  getEventEmitter<EventMap extends EventMapDefinition>(
    name: string
  ): EventEmitterDefinition<EventMap>;
  fetchOrCreateEventEmitter<EventMap extends EventMapDefinition>(
    name: string
  ): EventEmitterDefinition<EventMap>;
}
