import { AddBillEvent } from './add-bill-event';
import BudgetRegeneratedEventPayload from './definitions/budget-regenerated-event-payload';

export interface AddBillEventMap {
  [AddBillEvent.BUDGET_REGENERATED]: BudgetRegeneratedEventPayload;
}
