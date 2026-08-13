import { useEffect, useId, useRef, useState } from 'react';

import BudgetValueEditorProps from './types/budget-value-editor-props';
import { useDebouncedAction } from '../../../../util/hooks/use-debounced-action';
import { useMountedRef } from '../../../../util/hooks/use-mounted-ref';

import { centsToDollars } from 'lib/money/money';

import { useUpdateBudgetValue } from 'components/pages/dashboard/api/hooks/use-update-budget-value';
import { useBudgetValueEditorFormValidation } from 'components/pages/dashboard/validations/hooks/use-budget-value-editor-form-validation';

import MoneyInput from 'ui/form-elements/money-input';

const BudgetValueEditor = ({
  period_id,
  field,
  source_key,
  label,
  amount_cents,
  on_saved,
}: BudgetValueEditorProps) => {
  const inputId = useId();
  const editRevisionRef = useRef(0);
  const isMountedRef = useMountedRef();
  const isRequestInFlightRef = useRef(false);
  const hasPendingSaveRef = useRef(false);
  const synchronizedRevisionRef = useRef(0);
  const {
    requestData,
    getRequestData,
    setRequestData,
    error: requestError,
    updateValue,
  } = useUpdateBudgetValue({
    period_id,
    initial_request: {
      field,
      source_key,
      amount_dollars: centsToDollars(amount_cents),
      going_forward: false,
    },
  });
  const [status, setStatus] = useState('Saved');
  const [validationError, setValidationError] = useState<string | undefined>();
  const { validateBudgetValueEditor } = useBudgetValueEditorFormValidation();
  const { flush, schedule } = useDebouncedAction({
    action: persistLatest,
    delay_ms: 600,
  });

  useEffect(() => {
    const authoritativeAmount = centsToDollars(amount_cents);
    const hasLocalEdit =
      editRevisionRef.current !== synchronizedRevisionRef.current;

    if (
      hasLocalEdit ||
      isRequestInFlightRef.current ||
      hasPendingSaveRef.current
    ) {
      return;
    }

    setRequestData({
      ...getRequestData(),
      amount_dollars: authoritativeAmount,
      going_forward: false,
    });
  }, [amount_cents, getRequestData, setRequestData]);

  async function persistLatest(): Promise<void> {
    if (isRequestInFlightRef.current) {
      hasPendingSaveRef.current = true;

      return;
    }

    const submittedRevision = editRevisionRef.current;
    const submittedRequest = getRequestData();
    const validationResult = validateBudgetValueEditor(
      submittedRequest.field,
      submittedRequest.amount_dollars
    );

    if (!validationResult.is_valid) {
      if (isMountedRef.current) {
        let errorMessage = 'Enter a valid amount.';

        if (validationResult.field_errors.amount_dollars !== undefined) {
          errorMessage = validationResult.field_errors.amount_dollars;
        } else if (validationResult.step_error !== '') {
          errorMessage = validationResult.step_error;
        }

        setValidationError(errorMessage);
        setStatus('Save failed');
      }

      return;
    }

    isRequestInFlightRef.current = true;
    hasPendingSaveRef.current = false;

    if (isMountedRef.current) {
      setValidationError(undefined);
      setStatus('Saving');
    }

    try {
      const didUpdateValue = await updateValue();

      if (
        submittedRevision === editRevisionRef.current &&
        isMountedRef.current
      ) {
        if (didUpdateValue) {
          setStatus('Saved');
        } else {
          setStatus('Save failed');
        }
      }

      if (didUpdateValue) {
        if (submittedRevision === editRevisionRef.current) {
          synchronizedRevisionRef.current = submittedRevision;
          setRequestData({
            ...getRequestData(),
            going_forward: false,
          });
        }

        on_saved();
      }
    } finally {
      isRequestInFlightRef.current = false;

      if (
        hasPendingSaveRef.current ||
        submittedRevision !== editRevisionRef.current
      ) {
        hasPendingSaveRef.current = false;
        void persistLatest();
      }
    }
  }

  const handleValueChange = (nextValue: string) => {
    editRevisionRef.current += 1;
    setRequestData({
      ...requestData,
      amount_dollars: nextValue,
    });
    schedule();
  };

  const handleGoingForwardChange = () => {
    editRevisionRef.current += 1;
    setRequestData({
      ...requestData,
      going_forward: !requestData.going_forward,
    });
    schedule();
  };

  const getInputName = () => {
    if (source_key === undefined) {
      return `${field}-period`;
    }

    return `${field}-${source_key}`;
  };

  const getInputError = () => {
    if (validationError !== undefined) {
      return validationError;
    }

    if (status === 'Save failed' && requestError !== null) {
      return requestError;
    }

    return undefined;
  };

  const inputError = getInputError();

  return (
    <fieldset className="border-storm-dust-200 dark:border-storm-dust-700 space-y-3 rounded-xl border p-3">
      <MoneyInput
        id={inputId}
        name={getInputName()}
        label={label}
        value={requestData.amount_dollars}
        has_error={inputError !== undefined}
        error={inputError}
        on_value_change={handleValueChange}
        on_blur={flush}
      />

      <label className="text-storm-dust-700 dark:text-storm-dust-200 flex min-h-11 cursor-pointer items-center gap-3 text-sm">
        <input
          type="checkbox"
          checked={requestData.going_forward}
          onChange={handleGoingForwardChange}
          className="accent-blue-bell-700 h-5 w-5"
        />
        Apply {label} amount to this and future pay periods
      </label>

      <p
        aria-live="polite"
        className="text-storm-dust-500 dark:text-storm-dust-400 text-xs"
      >
        {status}
      </p>
    </fieldset>
  );
};

export default BudgetValueEditor;
