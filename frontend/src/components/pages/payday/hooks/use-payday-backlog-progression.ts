import { useState } from 'react';
import { useNavigate } from 'react-router';

import UsePaydayBacklogProgressionDefinition from './definitions/use-payday-backlog-progression-definition';

import { usePaydayQueueContext } from 'components/pages/payday/context/use-payday-queue-context';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { getPaydayRoute } from 'router/utils/get-payday-route';

export const usePaydayBacklogProgression = (
  periodId: number
): UsePaydayBacklogProgressionDefinition => {
  const navigate = useNavigate();
  const [isCaughtUp, setIsCaughtUp] = useState(false);
  const { refresh: refreshQueue } = usePaydayQueueContext();

  const finishPayday = async () => {
    const refreshedQueue = await refreshQueue();

    if (
      refreshedQueue !== null &&
      refreshedQueue.oldest_unresolved_period !== null
    ) {
      void navigate(
        getPaydayRoute(refreshedQueue.oldest_unresolved_period.id),
        { replace: true }
      );

      return true;
    }

    setIsCaughtUp(true);
    void navigate(NavigationRoutes.DASHBOARD, {
      replace: true,
      state: { focus_pay_period_id: periodId },
    });

    return true;
  };

  return {
    is_caught_up: isCaughtUp,
    finish_payday: finishPayday,
  };
};
