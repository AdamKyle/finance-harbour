import { FinanceHarbourScreen } from './enums/finance-harbour-screen';

export interface FHScreenMap {
  [FinanceHarbourScreen.BUDGET_BUILDING]: undefined;
  [FinanceHarbourScreen.BUDGET_DASHBOARD]: undefined;
  [FinanceHarbourScreen.HELP]: undefined;
  [FinanceHarbourScreen.PLAN_FUTURE_EXPENSES]: undefined;
  [FinanceHarbourScreen.DEBT_PROFILES]: undefined;
  [FinanceHarbourScreen.UPDATES]: undefined;
  [FinanceHarbourScreen.PAYDAY]: { period_id: number };
}
