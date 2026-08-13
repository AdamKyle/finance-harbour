import { ReactNode } from 'react';
import { Navigate, Outlet } from 'react-router';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { NavigationRoutes } from 'router/enums/navigation-routes';

const IncompleteRoute = (): ReactNode => {
  const { authenticatedUser, loading } = useAuthentication();

  if (loading) {
    return null;
  }

  if (authenticatedUser?.completed_onboarding) {
    return <Navigate replace to={NavigationRoutes.DASHBOARD} />;
  }

  return <Outlet />;
};

export default IncompleteRoute;
