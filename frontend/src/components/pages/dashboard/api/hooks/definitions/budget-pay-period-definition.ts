import { BudgetLineItemDefinition } from './budget-line-item-definition';

import PaydayDebtBalanceCheckDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-check-definition';
import {
  PayChequeReviewStatus,
  PaydayReconciliationStatus,
} from 'components/pages/payday/enums/payday-status';
import { PaymentCompletionStatus } from 'components/pages/payday/enums/payment-completion-status';

export interface BudgetPayPeriodDefinition {
  id: number;
  sequence: number;
  pay_date: string;
  previous_pay_date: string | null;
  pay_cheque_cents: number;
  pay_cheque_is_manual: boolean;
  carried_left_over_cents: number;
  carried_left_over_is_manual: boolean;
  total_available_cents: number;
  total_available_is_manual: boolean;
  total_bills_cents: number;
  total_bills_is_manual: boolean;
  left_over_cents: number;
  left_over_is_manual: boolean;
  has_negative_left_over: boolean;
  is_below_warning_threshold: boolean;
  has_deferred_items: boolean;
  affects_important_expenses: boolean;
  has_missed_important_expenses: boolean;
  payday_reconciliation_status: PaydayReconciliationStatus;
  actual_pay_cheque_cents: number | null;
  pay_cheque_review_status: PayChequeReviewStatus;
  pay_cheque_reconciled_at: string | null;
  payday_reconciliation_started_at: string | null;
  payday_reconciliation_completed_at: string | null;
  bill_count: number;
  paid_bill_count: number;
  scheduled_bill_count: number;
  missed_bill_count: number;
  payment_completion_percentage: number | null;
  payment_completion_status: PaymentCompletionStatus;
  debt_balance_checks: PaydayDebtBalanceCheckDefinition[];
  line_items: BudgetLineItemDefinition[];
}
