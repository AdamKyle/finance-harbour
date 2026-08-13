import { useEffect, useState } from 'react';

import BudgetPayDateEditorProps from './types/budget-pay-date-editor-props';

import { useUpdateBudgetPayDate } from 'components/pages/dashboard/api/hooks/use-update-budget-pay-date';
import {
  formatLocalIsoDate,
  getDayAfterLocalIsoDate,
  parseLocalIsoDate,
} from 'components/pages/dashboard/utils/local-date';
import { useBudgetPayDateValidation } from 'components/pages/dashboard/validations/hooks/use-budget-pay-date-validation';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import DateInput from 'ui/date-input/date-input';

const BudgetPayDateEditor = ({
  period,
  on_saved,
  on_close,
}: BudgetPayDateEditorProps) => {
  const [payDate, setPayDate] = useState(period.pay_date);
  const [validationError, setValidationError] = useState<string | undefined>();
  const {
    loading,
    error,
    update_pay_date: updatePayDate,
  } = useUpdateBudgetPayDate({ period_id: period.id });
  const { validate_pay_date: validatePayDate } = useBudgetPayDateValidation();

  useEffect(() => {
    setPayDate(period.pay_date);
    setValidationError(undefined);
  }, [period.pay_date]);

  let selectedDate: Date | undefined;
  let minimumDate = new Date();

  if (payDate !== '') {
    selectedDate = parseLocalIsoDate(payDate);
  }

  if (period.previous_pay_date !== null) {
    minimumDate = getDayAfterLocalIsoDate(period.previous_pay_date);
  }

  const handleDateChange = (date: Date | undefined) => {
    if (date === undefined) {
      setPayDate('');

      return;
    }

    setPayDate(formatLocalIsoDate(date));
    setValidationError(undefined);
  };

  const handleSave = async () => {
    const validationResult = validatePayDate(payDate, period.previous_pay_date);

    if (!validationResult.is_valid) {
      setValidationError(validationResult.error);

      return;
    }

    if (payDate === period.pay_date) {
      on_close();

      return;
    }

    const updatedPeriod = await updatePayDate(payDate);

    if (updatedPeriod === null) {
      return;
    }

    await on_saved(updatedPeriod.id);
    on_close();
  };

  const getSaveLabel = () => {
    if (loading) {
      return 'Regenerating budget';
    }

    return 'Save pay date';
  };

  const renderRequestError = () => {
    if (error === null) {
      return null;
    }

    return <Alert variant={AlertVariant.DANGER}>{error}</Alert>;
  };

  return (
    <fieldset className="border-storm-dust-200 dark:border-storm-dust-700 space-y-3 rounded-xl border p-3">
      <legend className="px-1 font-semibold">Pay-period cadence</legend>
      <DateInput
        id={`pay-date-${period.id}`}
        label="Pay date"
        selected={selectedDate}
        representative_month={selectedDate ?? minimumDate}
        minimum_date={minimumDate}
        error={validationError}
        help_text="Changing this date updates this pay period and regenerates all future pay periods. Earlier pay periods will not change."
        on_change={handleDateChange}
      />
      {renderRequestError()}
      <Button
        label={getSaveLabel()}
        variant={ButtonVariant.PRIMARY}
        disabled={loading}
        on_click={() => void handleSave()}
        additional_css="w-full"
      />
    </fieldset>
  );
};

export default BudgetPayDateEditor;
