import { ExpensePaymentTiming } from 'components/pages/onboarding/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/pages/onboarding/enums/paycheck-position';

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
