import { PayPeriodType } from 'components/payment-schedule/enums/pay-period-type';

export default interface RecurringObligationConfigurationDefinition {
  pay_period_type: PayPeriodType;
  representative_date: string;
}
