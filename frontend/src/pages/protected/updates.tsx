import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { FHScreenBindingHost } from 'configuration/screen-manager/screen-manager-kit';

const UpdatesPage = () => {
  return (
    <>
      <FHScreenBindingHost
        invocation={[FinanceHarbourScreen.BUDGET_DASHBOARD]}
        mode="reset"
      />
      <FHScreenBindingHost
        invocation={[FinanceHarbourScreen.UPDATES]}
        mode="push"
      />
    </>
  );
};

export default UpdatesPage;
