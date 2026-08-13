import { createContext } from 'react';

import EventSystemDefinition from './definitions/event-system-definition';

export const EventSystemContext = createContext<EventSystemDefinition | null>(
  null
);
