import { useId, useRef, useState } from 'react';

import BudgetPayDateEditor from './budget-pay-date-editor';
import BudgetValueEditor from './budget-value-editor';
import BudgetCardEditorProps from './types/budget-card-editor-props';
import { useFocusRequest } from '../../../../util/hooks/use-focus-request';

import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';
import { useAddBudgetBill } from 'components/pages/dashboard/api/hooks/use-add-budget-bill';
import AddBudgetBillFieldErrorsDefinition from 'components/pages/dashboard/validations/hooks/definitions/add-budget-bill-field-errors-definition';
import { useAddBudgetBillFormValidation } from 'components/pages/dashboard/validations/hooks/use-add-budget-bill-form-validation';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import Input from 'ui/form-elements/input';
import MoneyInput from 'ui/form-elements/money-input';

const BudgetCardEditor = ({
  period,
  line_items,
  on_close,
  on_saved,
  on_pay_date_saved,
  close_button_ref,
}: BudgetCardEditorProps) => {
  const billNameId = useId();
  const billAmountId = useId();
  const addBillErrorRef = useRef<HTMLDivElement>(null);
  const {
    requestData,
    setRequestData,
    loading: isAddingBill,
    error: addBillApiError,
    addBill,
  } = useAddBudgetBill({ period_id: period.id });
  const { validateAddBudgetBill } = useAddBudgetBillFormValidation();
  const [billStepError, setBillStepError] = useState('');
  const [billFieldErrors, setBillFieldErrors] =
    useState<AddBudgetBillFieldErrorsDefinition>({});
  const { request_focus: requestAddBillErrorFocus } = useFocusRequest({
    target_ref: addBillErrorRef,
    scroll_into_view: true,
  });

  const currentEntries = new Map(
    period.line_items.map((lineItem) => [lineItem.source_key, lineItem])
  );

  const handleAddBill = async () => {
    const validationResult = validateAddBudgetBill(requestData);

    if (!validationResult.is_valid) {
      setBillStepError(validationResult.step_error);
      setBillFieldErrors(validationResult.field_errors);
      requestAddBillErrorFocus();

      return;
    }

    setBillStepError('');
    setBillFieldErrors({});
    const didAddBill = await addBill();

    if (!didAddBill) {
      requestAddBillErrorFocus();

      return;
    }

    setRequestData({
      title: '',
      amount_dollars: '',
      is_required: false,
      going_forward: false,
    });
    on_saved();
  };

  const getAddBillErrorMessage = () => {
    if (billStepError !== '') {
      return billStepError;
    }

    if (addBillApiError !== null) {
      return addBillApiError;
    }

    return '';
  };

  const renderBillError = () => {
    const errorMessage = getAddBillErrorMessage();

    if (errorMessage === '') {
      return null;
    }

    return (
      <div ref={addBillErrorRef} tabIndex={-1} className="focus:outline-none">
        <Alert variant={AlertVariant.DANGER}>{errorMessage}</Alert>
      </div>
    );
  };

  const getAddBillLabel = () => {
    if (isAddingBill) {
      return 'Adding bill';
    }

    return 'Add bill';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">Edit budget values</h3>
        <IconButton
          icon="fa-solid fa-xmark"
          label="Close budget editor"
          aria_label="Close budget editor"
          variant={ButtonVariant.GHOST}
          on_click={on_close}
          button_ref={close_button_ref}
        />
      </div>

      <BudgetPayDateEditor
        period={period}
        on_saved={on_pay_date_saved}
        on_close={on_close}
      />

      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.PAY_CHEQUE}
        label="Pay cheque"
        amount_cents={period.pay_cheque_cents}
        on_saved={on_saved}
      />
      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.CARRIED_LEFT_OVER}
        label="Previous period left over"
        amount_cents={period.carried_left_over_cents}
        on_saved={on_saved}
      />
      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.TOTAL_AVAILABLE}
        label="Your total"
        amount_cents={period.total_available_cents}
        on_saved={on_saved}
      />

      {line_items.map((lineItem) => {
        const currentEntry = currentEntries.get(lineItem.source_key);
        let amountCents = 0;

        if (currentEntry !== undefined) {
          amountCents = currentEntry.amount_cents;
        }

        return (
          <BudgetValueEditor
            key={lineItem.source_key}
            period_id={period.id}
            field={BudgetValueField.LINE_ITEM}
            source_key={lineItem.source_key}
            label={lineItem.title}
            amount_cents={amountCents}
            on_saved={on_saved}
          />
        );
      })}

      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.TOTAL_BILLS}
        label="Total bills"
        amount_cents={period.total_bills_cents}
        on_saved={on_saved}
      />
      <BudgetValueEditor
        period_id={period.id}
        field={BudgetValueField.LEFT_OVER}
        label="Left over"
        amount_cents={period.left_over_cents}
        on_saved={on_saved}
      />

      <fieldset className="border-blue-bell-300 dark:border-blue-bell-700 space-y-3 rounded-xl border p-3">
        <legend className="px-1 font-semibold">Add a new bill</legend>
        <Input
          id={billNameId}
          name="new-bill-name"
          type="text"
          label="Bill name"
          value={requestData.title}
          has_error={billFieldErrors.title !== undefined}
          error={billFieldErrors.title}
          onChange={(event) =>
            setRequestData({
              ...requestData,
              title: event.target.value,
            })
          }
        />
        <MoneyInput
          id={billAmountId}
          name="new-bill-amount"
          label="Amount"
          value={requestData.amount_dollars}
          has_error={billFieldErrors.amount_dollars !== undefined}
          error={billFieldErrors.amount_dollars}
          on_value_change={(amountDollars) =>
            setRequestData({
              ...requestData,
              amount_dollars: amountDollars,
            })
          }
        />

        <label className="flex min-h-11 items-center gap-3 text-sm">
          <input
            type="checkbox"
            checked={requestData.is_required}
            onChange={() =>
              setRequestData({
                ...requestData,
                is_required: !requestData.is_required,
              })
            }
            className="accent-blue-bell-700 h-5 w-5"
          />
          Important bill
        </label>
        <label className="flex min-h-11 items-center gap-3 text-sm">
          <input
            type="checkbox"
            checked={requestData.going_forward}
            onChange={() =>
              setRequestData({
                ...requestData,
                going_forward: !requestData.going_forward,
              })
            }
            className="accent-blue-bell-700 h-5 w-5"
          />
          Add this bill to this and future pay periods
        </label>

        {renderBillError()}
        <Button
          label={getAddBillLabel()}
          aria_label="Add bill to budget"
          disabled={isAddingBill}
          variant={ButtonVariant.PRIMARY}
          on_click={() => void handleAddBill()}
          additional_css="w-full"
        />
      </fieldset>
    </div>
  );
};

export default BudgetCardEditor;
