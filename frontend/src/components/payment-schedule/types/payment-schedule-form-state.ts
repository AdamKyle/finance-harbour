import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';

export interface PaymentScheduleFormState {
  timing: ExpensePaymentTiming;
  paycheck_position: PaycheckPosition;
  day_of_month: string;
  auto_deducted: boolean | null;
}

export type CommonExpenseSourceKey =
  | 'rent_or_mortgage'
  | 'utilities'
  | 'food'
  | 'internet'
  | 'phone'
  | 'car_payment'
  | 'insurance';
