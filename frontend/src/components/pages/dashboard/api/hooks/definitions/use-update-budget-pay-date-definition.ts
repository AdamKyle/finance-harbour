import { BudgetPayPeriodDefinition } from './budget-pay-period-definition';

export default interface UseUpdateBudgetPayDateDefinition {
  loading: boolean;
  error: string | null;
  update_pay_date: (
    payDate: string
  ) => Promise<BudgetPayPeriodDefinition | null>;
}
