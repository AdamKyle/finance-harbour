import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';

export default interface UpdateBudgetPayDateApiRequestDefinition {
  field: BudgetValueField.PAY_DATE;
  pay_date: string;
}
