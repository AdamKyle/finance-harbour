import { useContext } from 'react';

import { PaydayQueueContext } from './payday-queue-context';

export const usePaydayQueueContext = () => {
  const context = useContext(PaydayQueueContext);

  if (context === null) {
    throw new Error(
      'usePaydayQueueContext must be used within PaydayQueueProvider'
    );
  }

  return context;
};
