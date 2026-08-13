import EventSystemProviderProps from './types/event-system-provider-props';

import EventSystemDefinition from 'lib/event-system/definitions/event-system-definition';
import { EventSystemContext } from 'lib/event-system/event-system-context';
import { serviceContainer } from 'lib/service-container/core-container';

export const EventSystemProvider = ({ children }: EventSystemProviderProps) => {
  const eventSystem =
    serviceContainer().fetch<EventSystemDefinition>('EventSystem');

  return (
    <EventSystemContext.Provider value={eventSystem}>
      {children}
    </EventSystemContext.Provider>
  );
};
