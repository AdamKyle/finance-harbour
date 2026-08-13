import { PayPeriodType } from 'components/payment-schedule/enums/pay-period-type';
import { PaymentScheduleFormState } from 'components/payment-schedule/types/payment-schedule-form-state';

export default interface PaymentScheduleFieldsProps {
  id: string;
  label: string;
  representative_date: string;
  pay_period_type: PayPeriodType | '';
  show_large_bill_hint?: boolean;
  schedule: PaymentScheduleFormState;
  on_change: (schedule: PaymentScheduleFormState) => void;
  error?: string;
}
