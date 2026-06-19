import LeftOverWarningStepProps from 'components/pages/onboarding/types/left-over-warning-step-props';

import MoneyInput from 'ui/form-elements/money-input';

const LeftOverWarningStep = ({
  request,
  setRequest,
  error,
}: LeftOverWarningStepProps) => {
  const handleValueChange = (value: string) => {
    setRequest({
      left_over_warning_amount_dollars: value,
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        If you have left over money, and you were to say use your debit card,
        whats your thresh hold before we warn you?
      </p>

      <MoneyInput
        id="left-over-warning-amount"
        label="Warning threshold"
        name="left_over_warning_amount_dollars"
        value={request.left_over_warning_amount_dollars}
        has_error={error !== undefined}
        error={error}
        on_value_change={handleValueChange}
        required
      />
    </div>
  );
};

export default LeftOverWarningStep;
