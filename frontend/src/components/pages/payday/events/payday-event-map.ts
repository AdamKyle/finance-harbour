import BudgetPeriodsRecalculatedEventPayload from './definitions/budget-periods-recalculated-event-payload';
import { PaydayEvent } from './payday-event';

export interface PaydayEventMap {
  [PaydayEvent.BUDGET_PERIODS_RECALCULATED]: BudgetPeriodsRecalculatedEventPayload;
}
