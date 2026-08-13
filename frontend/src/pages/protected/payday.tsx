import { Navigate, useParams } from 'react-router';

import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { FHScreenBindingHost } from 'configuration/screen-manager/screen-manager-kit';

import { NavigationRoutes } from 'router/enums/navigation-routes';

const PaydayPage = () => {
  const { periodId } = useParams();
  const parsedPeriodId =
    periodId === undefined ? Number.NaN : Number.parseInt(periodId, 10);
  const isValidPeriodId =
    Number.isInteger(parsedPeriodId) &&
    parsedPeriodId > 0 &&
    `${parsedPeriodId}` === periodId;

  if (!isValidPeriodId) {
    return <Navigate to={NavigationRoutes.DASHBOARD} replace />;
  }

  return (
    <FHScreenBindingHost
      invocation={[FinanceHarbourScreen.PAYDAY, { period_id: parsedPeriodId }]}
      mode="push"
    />
  );
};

export default PaydayPage;
