import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';
import { RecurringObligationKind } from 'components/side-peeks/add-bill/types/recurring-obligation-kind';

export default interface RecurringObligationApiRequestDefinition {
  kind: RecurringObligationKind;
  label: string;
  is_required: boolean;
  amount_cents?: number;
  current_balance_cents?: number;
  minimum_payment_cents?: number;
  current_payment_cents?: number;
  payment_schedule: {
    timing: ExpensePaymentTiming;
    paycheck_position: PaycheckPosition | null;
    day_of_month: number | null;
    auto_deducted: boolean;
  };
}
