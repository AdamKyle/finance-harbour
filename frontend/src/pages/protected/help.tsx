import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { FHScreenBindingHost } from 'configuration/screen-manager/screen-manager-kit';

const HelpPage = () => {
  return (
    <>
      <FHScreenBindingHost
        invocation={[FinanceHarbourScreen.BUDGET_DASHBOARD]}
        mode="reset"
      />
      <FHScreenBindingHost
        invocation={[FinanceHarbourScreen.HELP]}
        mode="push"
      />
    </>
  );
};

export default HelpPage;
