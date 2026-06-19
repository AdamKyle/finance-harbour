import { NavigateFunction } from 'react-router';

import { NavigationRoutes } from 'router/enums/navigation-routes';

export interface UseCompleteOnboardingParamsDefinition {
  navigate_to_route: (
    navigate: NavigateFunction,
    route: NavigationRoutes
  ) => void;
}
