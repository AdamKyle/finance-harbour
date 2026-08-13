import { PayChequeReviewStatus } from 'components/pages/payday/enums/payday-status';

export default interface PaydayPayChequeUpdateRequestDefinition {
  review_status: PayChequeReviewStatus;
  actual_amount_cents: number | null;
}
