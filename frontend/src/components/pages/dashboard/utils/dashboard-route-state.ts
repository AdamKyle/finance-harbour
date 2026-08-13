import DashboardRouteState from 'components/pages/dashboard/types/dashboard-route-state';

const isDashboardRouteState = (state: object): state is DashboardRouteState => {
  if (!('focus_pay_period_id' in state)) {
    return true;
  }

  return typeof state.focus_pay_period_id === 'number';
};

export const getDashboardFocusPeriodId = (
  state: object | null
): number | undefined => {
  if (state === null || !isDashboardRouteState(state)) {
    return undefined;
  }

  if (state.focus_pay_period_id === undefined) {
    return undefined;
  }

  return state.focus_pay_period_id;
};
