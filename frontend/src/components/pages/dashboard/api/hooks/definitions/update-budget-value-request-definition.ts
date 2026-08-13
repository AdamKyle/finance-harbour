import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';

export default interface UpdateBudgetValueRequestDefinition {
  field: BudgetValueField;
  source_key?: string;
  amount_dollars: string;
  going_forward: boolean;
}
