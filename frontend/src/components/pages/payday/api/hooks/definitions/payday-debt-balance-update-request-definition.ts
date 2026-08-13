import { DebtBalanceReviewStatus } from 'components/pages/payday/enums/payday-status';

export default interface PaydayDebtBalanceUpdateRequestDefinition {
  source_key: string;
  title: string;
  review_status: DebtBalanceReviewStatus;
  actual_balance_cents: number | null;
}
