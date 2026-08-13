import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { FHScreenBindingHost } from 'configuration/screen-manager/screen-manager-kit';

const DebtProfilesPage = () => {
  return (
    <FHScreenBindingHost
      invocation={[FinanceHarbourScreen.DEBT_PROFILES]}
      mode="push"
    />
  );
};

export default DebtProfilesPage;
