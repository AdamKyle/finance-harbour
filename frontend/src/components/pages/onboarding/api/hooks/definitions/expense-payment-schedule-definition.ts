import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';

export default interface ExpensePaymentScheduleDefinition {
  source_key: string;
  timing: ExpensePaymentTiming;
  paycheck_position: PaycheckPosition | null;
  day_of_month: number | null;
  auto_deducted: boolean;
}
