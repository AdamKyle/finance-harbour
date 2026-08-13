import { PaymentScheduleFormState } from 'components/payment-schedule/types/payment-schedule-form-state';

export interface DebtEntryFormState {
  label: string;
  current_balance_dollars: string;
  minimum_payment_dollars: string;
  current_payment_dollars: string;
  payment_schedule: PaymentScheduleFormState;
}

export type DebtEntryStringFieldName = keyof Pick<
  DebtEntryFormState,
  | 'label'
  | 'current_balance_dollars'
  | 'minimum_payment_dollars'
  | 'current_payment_dollars'
>;
