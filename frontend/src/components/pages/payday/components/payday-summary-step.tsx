import PaydayWarnings from './payday-warnings';
import PaydaySummaryStepProps from './types/payday-summary-step-props';

import {
  calculateFinancialVariance,
  formatCentsAsCurrency,
  formatFinancialVariance,
} from 'lib/money/money';

import { PaymentReviewStatus } from 'components/pages/payday/enums/payday-status';

const PaydaySummaryStep = ({ detail, warnings }: PaydaySummaryStepProps) => {
  const plannedPaymentCents = detail.pay_period.line_items.reduce(
    (total, lineItem) => total + lineItem.amount_cents,
    0
  );
  const knownActualPaymentCents = detail.pay_period.line_items.reduce(
    (total, lineItem) => {
      if (
        lineItem.payment_review_status !== PaymentReviewStatus.PAID ||
        lineItem.actual_amount_cents === null
      ) {
        return total;
      }

      return total + lineItem.actual_amount_cents;
    },
    0
  );
  const hasUnknownPayments = detail.pay_period.line_items.some(
    (lineItem) => lineItem.payment_review_status === PaymentReviewStatus.UNKNOWN
  );
  const variance = calculateFinancialVariance(
    plannedPaymentCents,
    knownActualPaymentCents
  );

  const renderPercentage = () => {
    if (detail.progress.payment_completion_percentage === null) {
      return <span>No bills due</span>;
    }

    return (
      <span>
        {detail.progress.payment_completion_percentage.toFixed(0)}% paid
      </span>
    );
  };

  const renderActualTotal = () => {
    if (hasUnknownPayments) {
      return (
        <p className="text-storm-dust-600 dark:text-storm-dust-300">
          Actual payment total is incomplete because one or more payments are
          unknown.
        </p>
      );
    }

    return (
      <>
        <p>Actual payments: {formatCentsAsCurrency(knownActualPaymentCents)}</p>
        <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
          {formatCentsAsCurrency(variance.difference_cents)} ·{' '}
          {formatFinancialVariance(variance)}
        </p>
      </>
    );
  };

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-xl font-bold">Payday review summary</h3>
        <p className="mt-2">
          {detail.progress.paid_bill_count} of {detail.progress.bill_count}{' '}
          bills paid · {renderPercentage()}
        </p>
        <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
          {detail.progress.scheduled_bill_count} still scheduled ·{' '}
          {detail.progress.missed_bill_count} missed
        </p>
      </div>
      <div className="space-y-2">
        <p>Planned payments: {formatCentsAsCurrency(plannedPaymentCents)}</p>
        {renderActualTotal()}
      </div>
      <PaydayWarnings warnings={warnings} />
    </div>
  );
};

export default PaydaySummaryStep;
