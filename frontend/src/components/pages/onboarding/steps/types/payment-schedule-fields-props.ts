import { PayPeriodType } from 'components/pages/onboarding/types/pay-period-type';
import { PaymentScheduleFormState } from 'components/pages/onboarding/types/payment-schedule-form-state';

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
