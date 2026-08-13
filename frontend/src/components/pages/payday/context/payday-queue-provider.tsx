import { useState } from 'react';

import { PaydayQueueContext } from './payday-queue-context';
import PaydayQueueProviderProps from './types/payday-queue-provider-props';

import { usePaydayQueue } from 'components/pages/payday/api/hooks/use-payday-queue';

const PaydayQueueProvider = ({ children }: PaydayQueueProviderProps) => {
  const paydayQueue = usePaydayQueue();
  const [dismissedEffectiveDate, setDismissedEffectiveDate] = useState<
    string | null
  >(null);
  const [dismissedUserId, setDismissedUserId] = useState<number | null>(null);

  const dismiss = (userId: number, effectiveDate: string) => {
    setDismissedUserId(userId);
    setDismissedEffectiveDate(effectiveDate);
  };

  return (
    <PaydayQueueContext.Provider
      value={{
        ...paydayQueue,
        dismissed_effective_date: dismissedEffectiveDate,
        dismissed_user_id: dismissedUserId,
        dismiss,
      }}
    >
      {children}
    </PaydayQueueContext.Provider>
  );
};

export default PaydayQueueProvider;
