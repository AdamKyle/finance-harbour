import { PayPeriodType } from 'components/payment-schedule/enums/pay-period-type';

export interface IncomeStepFormState {
  income_per_pay_period_dollars: string;
  pay_period_type: PayPeriodType | '';
  next_pay_date: string;
}
