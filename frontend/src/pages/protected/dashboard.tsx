import { Outlet } from 'react-router';

import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { FHScreenBindingHost } from 'configuration/screen-manager/screen-manager-kit';

const DashboardPage = () => {
  return (
    <>
      <FHScreenBindingHost
        invocation={[FinanceHarbourScreen.BUDGET_DASHBOARD]}
        mode="reset"
      />
      <Outlet />
    </>
  );
};

export default DashboardPage;
