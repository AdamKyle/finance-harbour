import { createContext } from 'react';

import PaydayQueueContextDefinition from './types/payday-queue-context-definition';

export const PaydayQueueContext =
  createContext<PaydayQueueContextDefinition | null>(null);
