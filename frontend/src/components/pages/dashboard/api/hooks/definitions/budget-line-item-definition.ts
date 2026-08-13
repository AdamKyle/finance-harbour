import { BudgetSourceType } from 'components/pages/dashboard/api/enums/budget-source-type';
import { ExpensePaymentTiming } from 'components/pages/onboarding/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/pages/onboarding/enums/paycheck-position';
import { PaymentReviewStatus } from 'components/pages/payday/enums/payday-status';

export interface BudgetLineItemDefinition {
  id: number;
  source_type: BudgetSourceType;
  source_key: string;
  title: string;
  amount_cents: number;
  display_order: number;
  is_required: boolean;
  is_split: boolean;
  is_manual_override: boolean;
  is_auto_deducted: boolean;
  funded_amount_cents: number;
  shortfall_cents: number;
  payment_review_status: PaymentReviewStatus;
  actual_amount_cents: number | null;
  scheduled_amount_cents: number | null;
  payment_reconciled_at: string | null;
  paid_at: string | null;
  expected_payment_date: string | null;
  payment_timing: ExpensePaymentTiming | '';
  paycheck_position: PaycheckPosition | '';
}
