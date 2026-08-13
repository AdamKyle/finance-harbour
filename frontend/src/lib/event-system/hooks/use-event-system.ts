import { useContext } from 'react';

import { EventSystemContext } from 'lib/event-system/event-system-context';

export const useEventSystem = () => {
  const eventSystem = useContext(EventSystemContext);

  if (eventSystem === null) {
    throw new Error('useEventSystem must be used within EventSystemProvider');
  }

  return eventSystem;
};
