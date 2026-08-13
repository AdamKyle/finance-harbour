import PaydayPayChequeStepProps from './types/payday-pay-cheque-step-props';

import {
  calculateFinancialVariance,
  centsToDollars,
  dollarsToCents,
  formatCentsAsCurrency,
  formatFinancialVariance,
} from 'lib/money/money';

import { PayChequeReviewStatus } from 'components/pages/payday/enums/payday-status';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import MoneyInput from 'ui/form-elements/money-input';

const PaydayPayChequeStep = ({
  planned_amount_cents,
  request,
  set_request,
  field_errors,
  allow_unknown,
  disabled,
}: PaydayPayChequeStepProps) => {
  const getActualAmountValue = () => {
    if (
      request.actual_amount_cents === null ||
      !Number.isFinite(request.actual_amount_cents)
    ) {
      return '';
    }

    return centsToDollars(request.actual_amount_cents);
  };

  const actualAmountValue = getActualAmountValue();

  const handleConfirmPlanned = () => {
    set_request({
      review_status: PayChequeReviewStatus.CONFIRMED,
      actual_amount_cents: planned_amount_cents,
    });
  };

  const handleActualAmountChange = (value: string) => {
    set_request({
      review_status: PayChequeReviewStatus.CONFIRMED,
      actual_amount_cents: dollarsToCents(value),
    });
  };

  const handleUnknown = () => {
    set_request({
      review_status: PayChequeReviewStatus.UNKNOWN,
      actual_amount_cents: null,
    });
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
        aria_pressed={request.review_status === PayChequeReviewStatus.UNKNOWN}
        additional_css="aria-pressed:ring-4 aria-pressed:ring-blue-bell-400"
      />
    );
  };

  const renderVariance = () => {
    if (
      request.review_status !== PayChequeReviewStatus.CONFIRMED ||
      request.actual_amount_cents === null ||
      !Number.isFinite(request.actual_amount_cents)
    ) {
      return null;
    }

    const variance = calculateFinancialVariance(
      planned_amount_cents,
      request.actual_amount_cents
    );

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Difference: {formatCentsAsCurrency(variance.difference_cents)} ·{' '}
        {formatFinancialVariance(variance)}
      </p>
    );
  };

  return (
    <div className="space-y-5">
      <p className="text-storm-dust-600 dark:text-storm-dust-300">
        Planned pay cheque: {formatCentsAsCurrency(planned_amount_cents)}
      </p>
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        <Button
          label="Confirm planned amount"
          variant={ButtonVariant.PRIMARY}
          disabled={disabled}
          on_click={handleConfirmPlanned}
          aria_pressed={
            request.review_status === PayChequeReviewStatus.CONFIRMED &&
            request.actual_amount_cents === planned_amount_cents
          }
          additional_css="aria-pressed:ring-4 aria-pressed:ring-blue-bell-400"
        />
        {renderUnknownButton()}
      </div>
      <MoneyInput
        id="payday-actual-pay-cheque"
        name="actual_pay_cheque"
        label="Actual pay cheque"
        value={actualAmountValue}
        has_error={field_errors.actual_amount_cents !== undefined}
        error={field_errors.actual_amount_cents}
        disabled={disabled}
        required={request.review_status === PayChequeReviewStatus.CONFIRMED}
        on_value_change={handleActualAmountChange}
      />
      {renderVariance()}
    </div>
  );
};

export default PaydayPayChequeStep;
