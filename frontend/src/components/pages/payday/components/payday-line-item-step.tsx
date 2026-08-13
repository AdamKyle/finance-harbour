import PaydayLineItemStepProps from './types/payday-line-item-step-props';

import {
  calculateFinancialVariance,
  centsToDollars,
  dollarsToCents,
  formatCentsAsCurrency,
  formatFinancialVariance,
} from 'lib/money/money';

import { PaymentReviewStatus } from 'components/pages/payday/enums/payday-status';
import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import MoneyInput from 'ui/form-elements/money-input';

const PaydayLineItemStep = ({
  line_item,
  request,
  set_request,
  field_errors,
  allow_unknown,
  disabled,
}: PaydayLineItemStepProps) => {
  const getActualAmountValue = () => {
    if (
      request.actual_amount_cents === null ||
      !Number.isFinite(request.actual_amount_cents)
    ) {
      return '';
    }

    return centsToDollars(request.actual_amount_cents);
  };

  const getScheduledAmountValue = () => {
    if (
      request.scheduled_amount_cents === null ||
      !Number.isFinite(request.scheduled_amount_cents)
    ) {
      return '';
    }

    return centsToDollars(request.scheduled_amount_cents);
  };
  const actualAmountValue = getActualAmountValue();
  const scheduledAmountValue = getScheduledAmountValue();

  const handlePaid = () => {
    let actualAmountCents = request.actual_amount_cents;

    if (
      request.review_status === PaymentReviewStatus.NOT_PAID ||
      request.review_status === PaymentReviewStatus.UNKNOWN ||
      request.review_status === PaymentReviewStatus.UNREVIEWED ||
      actualAmountCents === null ||
      !Number.isFinite(actualAmountCents)
    ) {
      actualAmountCents = line_item.amount_cents;

      if (
        line_item.payment_review_status === PaymentReviewStatus.PAID &&
        line_item.actual_amount_cents !== null
      ) {
        actualAmountCents = line_item.actual_amount_cents;
      }
    }

    set_request({
      review_status: PaymentReviewStatus.PAID,
      actual_amount_cents: actualAmountCents,
      scheduled_amount_cents: null,
    });
  };

  const handleNotPaid = () => {
    set_request({
      review_status: PaymentReviewStatus.NOT_PAID,
      actual_amount_cents: 0,
      scheduled_amount_cents: null,
    });
  };

  const handleUnknown = () => {
    set_request({
      review_status: PaymentReviewStatus.UNKNOWN,
      actual_amount_cents: null,
      scheduled_amount_cents: null,
    });
  };

  const handleScheduled = () => {
    set_request({
      review_status: PaymentReviewStatus.SCHEDULED,
      actual_amount_cents: null,
      scheduled_amount_cents:
        line_item.scheduled_amount_cents ?? line_item.amount_cents,
    });
  };

  const handleActualAmountChange = (value: string) => {
    set_request({
      review_status: PaymentReviewStatus.PAID,
      actual_amount_cents: dollarsToCents(value),
      scheduled_amount_cents: null,
    });
  };

  const handleScheduledAmountChange = (value: string) => {
    set_request({
      review_status: PaymentReviewStatus.SCHEDULED,
      actual_amount_cents: null,
      scheduled_amount_cents: dollarsToCents(value),
    });
  };

  const renderImportant = () => {
    if (!line_item.is_required) {
      return null;
    }

    return (
      <span className="bg-sweet-corn-100 text-sweet-corn-900 dark:bg-sweet-corn-900 dark:text-sweet-corn-100 inline-flex rounded-full px-2 py-1 text-xs font-bold">
        <i className="fa-solid fa-circle-exclamation mr-1" aria-hidden="true" />
        Important
      </span>
    );
  };

  const renderUnknownButton = () => {
    if (!allow_unknown) {
      return null;
    }

    return (
      <Button
        label="I don't remember"
        variant={ButtonVariant.Default}
        disabled={disabled}
        on_click={handleUnknown}
        aria_pressed={request.review_status === PaymentReviewStatus.UNKNOWN}
        additional_css="aria-pressed:ring-4 aria-pressed:ring-blue-bell-400"
      />
    );
  };

  const renderScheduledButton = () => {
    if (
      line_item.expected_payment_date === null ||
      line_item.payment_timing !== ExpensePaymentTiming.DAY_OF_MONTH
    ) {
      return null;
    }

    return (
      <Button
        label="Still scheduled"
        variant={ButtonVariant.Default}
        disabled={disabled}
        on_click={handleScheduled}
        aria_pressed={request.review_status === PaymentReviewStatus.SCHEDULED}
        additional_css="aria-pressed:ring-4 aria-pressed:ring-blue-bell-400"
      />
    );
  };

  const renderExpectedPayment = () => {
    if (
      line_item.expected_payment_date === null ||
      line_item.payment_timing !== ExpensePaymentTiming.DAY_OF_MONTH
    ) {
      return null;
    }

    const formattedDate = new Intl.DateTimeFormat('en-US', {
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC',
    }).format(new Date(`${line_item.expected_payment_date}T00:00:00Z`));

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300">
        {line_item.title} is expected to come out on {formattedDate}. Is this
        still correct?
      </p>
    );
  };

  const renderAmountInput = () => {
    if (request.review_status !== PaymentReviewStatus.PAID) {
      return null;
    }

    return (
      <MoneyInput
        id={`payday-line-item-${line_item.id}`}
        name={`line_item_${line_item.id}`}
        label="Actual amount paid"
        value={actualAmountValue}
        has_error={field_errors.actual_amount_cents !== undefined}
        error={field_errors.actual_amount_cents}
        disabled={disabled}
        required
        on_value_change={handleActualAmountChange}
      />
    );
  };

  const renderVariance = () => {
    if (
      request.review_status !== PaymentReviewStatus.PAID ||
      request.actual_amount_cents === null ||
      !Number.isFinite(request.actual_amount_cents)
    ) {
      return null;
    }

    const variance = calculateFinancialVariance(
      line_item.amount_cents,
      request.actual_amount_cents
    );

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Actual {formatCentsAsCurrency(request.actual_amount_cents)} ·{' '}
        {formatFinancialVariance(variance)} · Paid
      </p>
    );
  };

  const renderScheduledAmountInput = () => {
    if (request.review_status !== PaymentReviewStatus.SCHEDULED) {
      return null;
    }

    return (
      <MoneyInput
        id={`payday-line-item-scheduled-${line_item.id}`}
        name={`line_item_scheduled_${line_item.id}`}
        label="Expected amount"
        value={scheduledAmountValue}
        has_error={field_errors.scheduled_amount_cents !== undefined}
        error={field_errors.scheduled_amount_cents}
        disabled={disabled}
        required
        on_value_change={handleScheduledAmountChange}
      />
    );
  };

  const renderScheduledVariance = () => {
    if (
      request.review_status !== PaymentReviewStatus.SCHEDULED ||
      request.scheduled_amount_cents === null ||
      !Number.isFinite(request.scheduled_amount_cents)
    ) {
      return null;
    }

    const variance = calculateFinancialVariance(
      line_item.amount_cents,
      request.scheduled_amount_cents
    );

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Scheduled {formatCentsAsCurrency(request.scheduled_amount_cents)} ·{' '}
        {formatFinancialVariance(variance)}
      </p>
    );
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-semibold">{line_item.title}</p>
        {renderImportant()}
      </div>
      <p className="text-storm-dust-600 dark:text-storm-dust-300">
        Planned payment: {formatCentsAsCurrency(line_item.amount_cents)}
      </p>
      {renderExpectedPayment()}
      <div
        className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
        role="group"
        aria-label={`Payment result for ${line_item.title}`}
      >
        <Button
          label="Paid"
          variant={ButtonVariant.SUCCESS}
          disabled={disabled}
          on_click={handlePaid}
          aria_pressed={request.review_status === PaymentReviewStatus.PAID}
          additional_css="aria-pressed:ring-4 aria-pressed:ring-tom-thumb-400"
        />
        <Button
          label="Not paid"
          variant={ButtonVariant.DANGER}
          disabled={disabled}
          on_click={handleNotPaid}
          aria_pressed={request.review_status === PaymentReviewStatus.NOT_PAID}
          additional_css="aria-pressed:ring-4 aria-pressed:ring-persian-plum-400"
        />
        {renderScheduledButton()}
        {renderUnknownButton()}
      </div>
      {renderAmountInput()}
      {renderScheduledAmountInput()}
      {renderVariance()}
      {renderScheduledVariance()}
    </div>
  );
};

export default PaydayLineItemStep;
