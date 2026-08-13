import {
  PaydayWarningSeverity,
  PaydayWarningType,
} from 'components/pages/payday/enums/payday-warning';

export default interface PaydayWarningDefinition {
  warning_type: PaydayWarningType;
  affected_period_id: number;
  affected_pay_date: string;
  amount_cents: number | null;
  important_titles: string[];
  severity: PaydayWarningSeverity;
}
