import { DebtBalanceReviewStatus } from 'components/pages/payday/enums/payday-status';

export default interface PaydayDebtBalanceCheckDefinition {
  source_key: string;
  title: string;
  expected_balance_cents: number | null;
  actual_balance_cents: number | null;
  review_status: DebtBalanceReviewStatus;
  variance_cents: number | null;
  variance_percentage: number | null;
  previous_confirmed_balance_cents: number | null;
  movement_from_previous_percentage: number | null;
  is_uncertain: boolean;
}
