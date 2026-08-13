import { PaymentScheduleFormState } from './payment-schedule-form-state';

export interface MiscExpenseEntryFormState {
  label: string;
  amount_dollars: string;
  payment_schedule: PaymentScheduleFormState;
}
