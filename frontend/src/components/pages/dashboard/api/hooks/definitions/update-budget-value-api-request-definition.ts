import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';

export default interface UpdateBudgetValueApiRequestDefinition {
  field: BudgetValueField;
  source_key?: string;
  amount_cents: number;
  going_forward: boolean;
}
