import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router';

import { usePaydayQueueContext } from './context/use-payday-queue-context';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { getPaydayRoute } from 'router/utils/get-payday-route';

const PaydayAutoNavigator = () => {
  const { queue, loading, dismissed_effective_date, dismissed_user_id } =
    usePaydayQueueContext();
  const { authenticatedUser } = useAuthentication();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (
      loading ||
      queue?.oldest_unresolved_period === null ||
      queue === null ||
      authenticatedUser === null
    ) {
      return;
    }

    if (location.pathname.startsWith('/dashboard/payday/')) {
      return;
    }

    if (location.pathname !== NavigationRoutes.DASHBOARD) {
      return;
    }

    if (
      dismissed_user_id === authenticatedUser.id &&
      dismissed_effective_date === queue.effective_date
    ) {
      return;
    }

    void navigate(getPaydayRoute(queue.oldest_unresolved_period.id));
  }, [
    authenticatedUser,
    dismissed_effective_date,
    dismissed_user_id,
    loading,
    location.pathname,
    navigate,
    queue,
  ]);

  return null;
};

export default PaydayAutoNavigator;
