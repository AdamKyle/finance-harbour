import { useEffect } from 'react';

import UsePaydayDashboardRefreshParams from './definitions/use-payday-dashboard-refresh-params';

import { useEventSystem } from 'lib/event-system/hooks/use-event-system';

import BudgetPeriodsRecalculatedEventPayload from 'components/pages/payday/events/definitions/budget-periods-recalculated-event-payload';
import { PaydayEvent } from 'components/pages/payday/events/payday-event';
import { PaydayEventEmitterName } from 'components/pages/payday/events/payday-event-emitter-name';
import { PaydayEventMap } from 'components/pages/payday/events/payday-event-map';

export const usePaydayDashboardRefresh = ({
  refresh_dashboard,
}: UsePaydayDashboardRefreshParams) => {
  const eventSystem = useEventSystem();

  useEffect(() => {
    const emitter = eventSystem.fetchOrCreateEventEmitter<PaydayEventMap>(
      PaydayEventEmitterName.PAYDAY
    );
    const handlePaydayBudgetUpdated = (
      _payload: BudgetPeriodsRecalculatedEventPayload
    ) => {
      refresh_dashboard().catch(() => {});
    };

    emitter.on(
      PaydayEvent.BUDGET_PERIODS_RECALCULATED,
      handlePaydayBudgetUpdated
    );

    return () => {
      emitter.off(
        PaydayEvent.BUDGET_PERIODS_RECALCULATED,
        handlePaydayBudgetUpdated
      );
    };
  }, [eventSystem, refresh_dashboard]);
};
