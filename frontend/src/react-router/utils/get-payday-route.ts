import { NavigationRoutes } from 'router/enums/navigation-routes';

/**
 * Builds the protected Payday route for a validated positive period identifier.
 *
 * @param periodId - Budget pay-period identifier.
 * @returns Concrete Payday route.
 * @throws This function does not throw.
 */
export const getPaydayRoute = (periodId: number): string => {
  return NavigationRoutes.PAYDAY.replace(':periodId', `${periodId}`);
};
