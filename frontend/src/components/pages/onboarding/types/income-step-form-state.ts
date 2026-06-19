import { PayPeriodType } from './pay-period-type';

export interface IncomeStepFormState {
  income_per_pay_period_dollars: string;
  pay_period_type: PayPeriodType | '';
}
