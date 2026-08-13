import PaydayDebtBalanceStepProps from './types/payday-debt-balance-step-props';

import {
  calculateFinancialVariance,
  centsToDollars,
  dollarsToCents,
  formatCentsAsCurrency,
  formatFinancialVariance,
} from 'lib/money/money';

import { DebtBalanceReviewStatus } from 'components/pages/payday/enums/payday-status';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import MoneyInput from 'ui/form-elements/money-input';

const PaydayDebtBalanceStep = ({
  balance_check,
  request,
  set_request,
  field_errors,
  allow_unknown,
  disabled,
}: PaydayDebtBalanceStepProps) => {
  const getActualBalanceValue = () => {
    if (
      request.actual_balance_cents === null ||
      !Number.isFinite(request.actual_balance_cents)
    ) {
      return '';
    }

    return centsToDollars(request.actual_balance_cents);
  };

  const handleConfirm = () => {
    let actualBalanceCents = request.actual_balance_cents;

    if (actualBalanceCents === null || !Number.isFinite(actualBalanceCents)) {
      actualBalanceCents = balance_check.expected_balance_cents;
    }

    set_request({
      source_key: balance_check.source_key,
      title: balance_check.title,
      review_status: DebtBalanceReviewStatus.CONFIRMED,
      actual_balance_cents: actualBalanceCents,
    });
  };

  const handleUnknown = () => {
    set_request({
      source_key: balance_check.source_key,
      title: balance_check.title,
      review_status: DebtBalanceReviewStatus.UNKNOWN,
      actual_balance_cents: null,
    });
  };

  const handleActualBalanceChange = (value: string) => {
    set_request({
      source_key: balance_check.source_key,
      title: balance_check.title,
      review_status: DebtBalanceReviewStatus.CONFIRMED,
      actual_balance_cents: dollarsToCents(value),
    });
  };

  const renderExpectedBalance = () => {
    if (balance_check.expected_balance_cents === null) {
      return (
        <p className="text-storm-dust-600 dark:text-storm-dust-300">
          Expected balance unavailable
        </p>
      );
    }

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300">
        Expected balance:{' '}
        {formatCentsAsCurrency(balance_check.expected_balance_cents)}
      </p>
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
        aria_pressed={request.review_status === DebtBalanceReviewStatus.UNKNOWN}
        additional_css="aria-pressed:ring-4 aria-pressed:ring-blue-bell-400"
      />
    );
  };

  const renderVariance = () => {
    if (
      balance_check.expected_balance_cents === null ||
      request.actual_balance_cents === null ||
      !Number.isFinite(request.actual_balance_cents)
    ) {
      return null;
    }

    const variance = calculateFinancialVariance(
      balance_check.expected_balance_cents,
      request.actual_balance_cents
    );

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Balance difference: {formatCentsAsCurrency(variance.difference_cents)} ·{' '}
        {formatFinancialVariance(variance)}
      </p>
    );
  };

  const renderBalanceMovement = () => {
    const movement = balance_check.movement_from_previous_percentage;

    if (movement === null) {
      return null;
    }

    let direction = 'down';

    if (movement >= 0) {
      direction = 'up';
    }

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Balance {direction} {Math.abs(movement).toFixed(1)}% since the last
        confirmed balance.
      </p>
    );
  };

  return (
    <div className="space-y-5">
      <div>
        <p className="font-semibold">{balance_check.title} balance</p>
        {renderExpectedBalance()}
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        <Button
          label="Confirm balance"
          variant={ButtonVariant.PRIMARY}
          disabled={disabled}
          on_click={handleConfirm}
          aria_pressed={
            request.review_status === DebtBalanceReviewStatus.CONFIRMED
          }
          additional_css="aria-pressed:ring-4 aria-pressed:ring-blue-bell-400"
        />
        {renderUnknownButton()}
      </div>
      <MoneyInput
        id={`payday-debt-balance-${balance_check.source_key}`}
        name={`debt_balance_${balance_check.source_key}`}
        label="Actual balance"
        value={getActualBalanceValue()}
        has_error={field_errors.actual_balance_cents !== undefined}
        error={field_errors.actual_balance_cents}
        disabled={disabled}
        required={request.review_status === DebtBalanceReviewStatus.CONFIRMED}
        on_value_change={handleActualBalanceChange}
      />
      {renderVariance()}
      {renderBalanceMovement()}
    </div>
  );
};

export default PaydayDebtBalanceStep;
