import { PaymentReviewStatus } from 'components/pages/payday/enums/payday-status';

export default interface PaydayLineItemUpdateRequestDefinition {
  review_status: PaymentReviewStatus;
  actual_amount_cents: number | null;
  scheduled_amount_cents: number | null;
}
