import { PaymentScheduleFormState } from 'components/payment-schedule/types/payment-schedule-form-state';
import { RecurringObligationKind } from 'components/side-peeks/add-bill/types/recurring-obligation-kind';

export default interface AddBillFormRequestDefinition {
  kind: RecurringObligationKind | '';
  label: string;
  amount_dollars: string;
  current_balance_dollars: string;
  minimum_payment_dollars: string;
  current_payment_dollars: string;
  is_required: boolean;
  payment_schedule: PaymentScheduleFormState;
}
