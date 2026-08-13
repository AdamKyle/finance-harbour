import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { FHScreenBindingHost } from 'configuration/screen-manager/screen-manager-kit';

const PlanFutureExpensesPage = () => {
  return (
    <FHScreenBindingHost
      invocation={[FinanceHarbourScreen.PLAN_FUTURE_EXPENSES]}
      mode="push"
    />
  );
};

export default PlanFutureExpensesPage;
