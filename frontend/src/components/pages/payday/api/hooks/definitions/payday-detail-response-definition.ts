import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';
import PaydayDebtBalanceCheckDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-check-definition';
import { PaydayReconciliationStatus } from 'components/pages/payday/enums/payday-status';
import { PaymentCompletionStatus } from 'components/pages/payday/enums/payment-completion-status';

export interface PaydayProgressDefinition {
  bill_count: number;
  reviewed_bill_count: number;
  paid_bill_count: number;
  scheduled_bill_count: number;
  missed_bill_count: number;
  payment_completion_percentage: number | null;
  payment_completion_status: PaymentCompletionStatus;
  overall_reconciliation_status: PaydayReconciliationStatus;
}

export type { default as PaydayDebtBalanceCheckDefinition } from './payday-debt-balance-check-definition';

export default interface PaydayDetailResponseDefinition {
  pay_period: BudgetPayPeriodDefinition;
  debt_balance_checks: PaydayDebtBalanceCheckDefinition[];
  progress: PaydayProgressDefinition;
}
