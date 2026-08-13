import { BudgetLineItemDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-line-item-definition';
import { BudgetPayPeriodDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-pay-period-definition';
import PaydayDebtBalanceCheckDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-check-definition';
import PaydayDebtBalanceUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-debt-balance-update-request-definition';
import PaydayLineItemUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-line-item-update-request-definition';
import PaydayPayChequeUpdateRequestDefinition from 'components/pages/payday/api/hooks/definitions/payday-pay-cheque-update-request-definition';
import {
  DebtBalanceReviewStatus,
  PayChequeReviewStatus,
  PaydayReconciliationStatus,
  PaymentReviewStatus,
} from 'components/pages/payday/enums/payday-status';

/**
 * Builds the initial pay-cheque request from the persisted fact.
 * @param period - Persisted Payday period.
 * @returns Typed pay-cheque mutation request.
 * @throws This function does not throw.
 */
export const buildInitialPayChequeRequest = (
  period: BudgetPayPeriodDefinition
): PaydayPayChequeUpdateRequestDefinition => {
  return {
    review_status: period.pay_cheque_review_status,
    actual_amount_cents: period.actual_pay_cheque_cents,
  };
};

/**
 * Builds the initial line-item request for the first unresolved fact.
 * @param lineItems - Persisted ordered bill facts.
 * @returns Typed line-item mutation request.
 * @throws This function does not throw.
 */
export const buildInitialLineItemRequest = (
  lineItems: BudgetLineItemDefinition[]
): PaydayLineItemUpdateRequestDefinition => {
  const selectedLineItem =
    lineItems.find(
      (lineItem) =>
        lineItem.payment_review_status === PaymentReviewStatus.UNREVIEWED ||
        lineItem.payment_review_status === PaymentReviewStatus.UNKNOWN
    ) ?? lineItems[0];

  if (selectedLineItem === undefined) {
    return {
      review_status: PaymentReviewStatus.UNREVIEWED,
      actual_amount_cents: null,
      scheduled_amount_cents: null,
    };
  }

  return {
    review_status: selectedLineItem.payment_review_status,
    actual_amount_cents: selectedLineItem.actual_amount_cents,
    scheduled_amount_cents: selectedLineItem.scheduled_amount_cents,
  };
};

/**
 * Builds the initial debt request for the first unresolved balance fact.
 * @param balanceChecks - Persisted and projected debt facts.
 * @returns Typed debt-balance mutation request.
 * @throws This function does not throw.
 */
export const buildInitialDebtBalanceRequest = (
  balanceChecks: PaydayDebtBalanceCheckDefinition[]
): PaydayDebtBalanceUpdateRequestDefinition => {
  const selectedBalance =
    balanceChecks.find(
      (balanceCheck) =>
        balanceCheck.review_status === DebtBalanceReviewStatus.UNREVIEWED ||
        balanceCheck.review_status === DebtBalanceReviewStatus.UNKNOWN
    ) ?? balanceChecks[0];

  if (selectedBalance === undefined) {
    return {
      source_key: '',
      title: '',
      review_status: DebtBalanceReviewStatus.UNREVIEWED,
      actual_balance_cents: null,
    };
  }

  return {
    source_key: selectedBalance.source_key,
    title: selectedBalance.title,
    review_status: selectedBalance.review_status,
    actual_balance_cents: selectedBalance.actual_balance_cents,
  };
};

/**
 * Finds the first unreviewed or unknown fact when resuming Payday history.
 * @param period - Persisted Payday period.
 * @param lineItems - Ordered bill facts.
 * @param balanceChecks - Ordered debt-balance facts.
 * @returns Zero-based wizard step index.
 * @throws This function does not throw.
 */
export const getPaydayResumeIndex = (
  period: BudgetPayPeriodDefinition,
  lineItems: BudgetLineItemDefinition[],
  balanceChecks: PaydayDebtBalanceCheckDefinition[]
): number => {
  if (
    period.payday_reconciliation_status === PaydayReconciliationStatus.REVIEWED
  ) {
    const notPaidIndex = lineItems.findIndex(
      (lineItem) =>
        lineItem.payment_review_status === PaymentReviewStatus.NOT_PAID
    );

    if (notPaidIndex >= 0) {
      return notPaidIndex + 1;
    }
  }

  if (
    period.pay_cheque_review_status === PayChequeReviewStatus.UNREVIEWED ||
    period.pay_cheque_review_status === PayChequeReviewStatus.UNKNOWN
  ) {
    return 0;
  }

  const lineItemIndex = lineItems.findIndex(
    (lineItem) =>
      lineItem.payment_review_status === PaymentReviewStatus.UNREVIEWED ||
      lineItem.payment_review_status === PaymentReviewStatus.UNKNOWN
  );

  if (lineItemIndex >= 0) {
    return lineItemIndex + 1;
  }

  const firstDebtIndex = lineItems.length + 1;
  const debtIndex = balanceChecks.findIndex(
    (balanceCheck) =>
      balanceCheck.review_status === DebtBalanceReviewStatus.UNREVIEWED ||
      balanceCheck.review_status === DebtBalanceReviewStatus.UNKNOWN
  );

  if (debtIndex >= 0) {
    return firstDebtIndex + debtIndex;
  }

  return firstDebtIndex + balanceChecks.length;
};
