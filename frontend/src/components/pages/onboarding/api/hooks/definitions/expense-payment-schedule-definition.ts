import { ExpensePaymentTiming } from 'components/pages/onboarding/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/pages/onboarding/enums/paycheck-position';

export default interface ExpensePaymentScheduleDefinition {
  source_key: string;
  timing: ExpensePaymentTiming;
  paycheck_position: PaycheckPosition | null;
  day_of_month: number | null;
  auto_deducted: boolean;
}
