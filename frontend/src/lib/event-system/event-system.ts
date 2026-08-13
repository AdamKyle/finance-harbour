import EventEmitterDefinition from './definitions/event-emitter-definition';
import { EventMapDefinition } from './definitions/event-map-definition';
import EventSystemDefinition from './definitions/event-system-definition';
import EventEmitter from './event-emitter';

export default class EventSystem implements EventSystemDefinition {
  private readonly registeredNames = new Set<string>();
  private readonly emitters = new Map<string, EventEmitter<object>>();

  isEventRegistered(name: string): boolean {
    return this.registeredNames.has(name);
  }

  registerEvent(name: string): void {
    if (this.isEventRegistered(name)) {
      return;
    }

    this.registeredNames.add(name);
    this.emitters.set(name, new EventEmitter<object>());
  }

  getEventEmitter<EventMap extends EventMapDefinition>(
    name: string
  ): EventEmitterDefinition<EventMap> {
    const emitter = this.emitters.get(name);

    if (emitter === undefined) {
      throw new Error(`Event emitter ${name} is not registered.`);
    }

    return emitter;
  }

  fetchOrCreateEventEmitter<EventMap extends EventMapDefinition>(
    name: string
  ): EventEmitterDefinition<EventMap> {
    this.registerEvent(name);

    return this.getEventEmitter<EventMap>(name);
  }
}
