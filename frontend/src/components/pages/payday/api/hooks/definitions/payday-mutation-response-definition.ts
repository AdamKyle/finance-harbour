import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';
import PaydayWarningDefinition from 'components/pages/payday/api/hooks/definitions/payday-warning-definition';

export default interface PaydayMutationResponseDefinition {
  pay_period: BudgetPayPeriodDefinition;
  warnings: PaydayWarningDefinition[];
  affected_pay_period_ids: number[];
}
