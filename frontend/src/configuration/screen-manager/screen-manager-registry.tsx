import { FinanceHarbourScreen } from './enums/finance-harbour-screen';
import { FHScreenMap } from './screen-manager-props';

import { RegistryType } from 'lib/screen-manager/types/registry-type';

import BudgetBuildingScreen from 'components/pages/budget-building/budget-building-screen';
import Dashboard from 'components/pages/dashboard/dashboard';
import DebtProfilesScreen from 'components/pages/debt-profiles/debt-profiles-screen';
import PaydayScreen from 'components/pages/payday/payday-screen';
import PlanFutureExpensesScreen from 'components/pages/plan-future-expenses/plan-future-expenses-screen';

import Help from 'pages/public/help';
import Updates from 'pages/public/updates';

export const resolveFHScreen: RegistryType<FHScreenMap> = (...invocation) => {
  const screen = invocation[0];

  switch (screen) {
    case FinanceHarbourScreen.BUDGET_BUILDING:
      return {
        screenName: FinanceHarbourScreen.BUDGET_BUILDING,
        dismissible: false,
        renderContent: () => <BudgetBuildingScreen />,
      };

    case FinanceHarbourScreen.BUDGET_DASHBOARD:
      return {
        screenName: FinanceHarbourScreen.BUDGET_DASHBOARD,
        dismissible: false,
        renderContent: () => <Dashboard />,
      };

    case FinanceHarbourScreen.HELP:
      return {
        screenName: FinanceHarbourScreen.HELP,
        dismissible: false,
        renderContent: () => <Help />,
      };

    case FinanceHarbourScreen.PLAN_FUTURE_EXPENSES:
      return {
        screenName: FinanceHarbourScreen.PLAN_FUTURE_EXPENSES,
        dismissible: false,
        renderContent: () => <PlanFutureExpensesScreen />,
      };

    case FinanceHarbourScreen.DEBT_PROFILES:
      return {
        screenName: FinanceHarbourScreen.DEBT_PROFILES,
        dismissible: false,
        renderContent: () => <DebtProfilesScreen />,
      };

    case FinanceHarbourScreen.UPDATES:
      return {
        screenName: FinanceHarbourScreen.UPDATES,
        dismissible: false,
        renderContent: () => <Updates />,
      };

    case FinanceHarbourScreen.PAYDAY: {
      const props = invocation[1];

      return {
        screenName: FinanceHarbourScreen.PAYDAY,
        dismissible: false,
        renderContent: () => <PaydayScreen period_id={props.period_id} />,
      };
    }
  }
};
