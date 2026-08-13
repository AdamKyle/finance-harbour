import { useEffect } from 'react';

import UseAddBillDashboardRefreshParams from './definitions/use-add-bill-dashboard-refresh-params';

import { useEventSystem } from 'lib/event-system/hooks/use-event-system';

import { AddBillEvent } from 'components/side-peeks/add-bill/events/add-bill-event';
import { AddBillEventEmitterName } from 'components/side-peeks/add-bill/events/add-bill-event-emitter-name';
import { AddBillEventMap } from 'components/side-peeks/add-bill/events/add-bill-event-map';

export const useAddBillDashboardRefresh = ({
  refresh_dashboard,
}: UseAddBillDashboardRefreshParams) => {
  const eventSystem = useEventSystem();

  useEffect(() => {
    const emitter = eventSystem.fetchOrCreateEventEmitter<AddBillEventMap>(
      AddBillEventEmitterName.ADD_BILL
    );
    const handleBudgetRegenerated = () => {
      void refresh_dashboard();
    };

    emitter.on(AddBillEvent.BUDGET_REGENERATED, handleBudgetRegenerated);

    return () => {
      emitter.off(AddBillEvent.BUDGET_REGENERATED, handleBudgetRegenerated);
    };
  }, [eventSystem, refresh_dashboard]);
};
