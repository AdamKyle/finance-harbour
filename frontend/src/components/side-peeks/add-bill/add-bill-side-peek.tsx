import { ChangeEvent, useRef, useState } from 'react';

import { useRecurringObligation } from './api/hooks/use-recurring-obligation';
import { AddBillEvent } from './events/add-bill-event';
import { AddBillEventEmitterName } from './events/add-bill-event-emitter-name';
import { AddBillEventMap } from './events/add-bill-event-map';
import AddBillFieldErrorsDefinition from './validations/hooks/definitions/add-bill-field-errors-definition';
import { useAddBillFormValidation } from './validations/hooks/use-add-bill-form-validation';

import { useFHSidePeekNavigation } from 'configuration/side-peek/side-peek-kit';

import { useEventSystem } from 'lib/event-system/hooks/use-event-system';
import { formatCentsAsCurrency, dollarsToCents } from 'lib/money/money';

import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import PaymentScheduleFields from 'components/payment-schedule/payment-schedule-fields';
import { RecurringObligationKind } from 'components/side-peeks/add-bill/types/recurring-obligation-kind';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Input from 'ui/form-elements/input';
import MoneyInput from 'ui/form-elements/money-input';
import Select from 'ui/form-elements/select';
import FormWizard from 'ui/form-wizard/form-wizard';
import Step from 'ui/form-wizard/step';

import { useFocusRequest } from 'util/hooks/use-focus-request';

const AddBillSidePeek = () => {
  const eventSystem = useEventSystem();
  const { pop } = useFHSidePeekNavigation();
  const { requestData, setRequestData, configuration, loading, error, save } =
    useRecurringObligation();
  const { validateStep, validateAll } = useAddBillFormValidation();
  const [stepError, setStepError] = useState('');
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [fieldErrors, setFieldErrors] = useState<AddBillFieldErrorsDefinition>(
    {}
  );
  const errorRef = useRef<HTMLDivElement>(null);
  const { request_focus: requestErrorFocus } = useFocusRequest({
    target_ref: errorRef,
    scroll_into_view: true,
  });

  const updateKind = (event: ChangeEvent<HTMLSelectElement>) => {
    let kind: RecurringObligationKind | '' = '';

    if (event.target.value === RecurringObligationKind.BILL) {
      kind = RecurringObligationKind.BILL;
    } else if (event.target.value === RecurringObligationKind.DEBT) {
      kind = RecurringObligationKind.DEBT;
    }

    setRequestData({ ...requestData, kind });
  };

  const handleNext = async (step: number) => {
    let validation = validateStep(step, requestData);

    if (step === 3) {
      validation = validateAll(requestData);
    }
    setStepError(validation.step_error);
    setFieldErrors(validation.field_errors);

    if (!validation.is_valid) {
      requestErrorFocus();

      return false;
    }

    if (step !== 3) {
      setCurrentStepIndex(step + 1);

      return true;
    }

    const response = await save();

    if (response === null) {
      requestErrorFocus();

      return false;
    }

    eventSystem
      .fetchOrCreateEventEmitter<AddBillEventMap>(
        AddBillEventEmitterName.ADD_BILL
      )
      .emit(AddBillEvent.BUDGET_REGENERATED, {
        effective_period_id: response.first_effective_budget_period_id,
      });
    pop();

    return true;
  };

  const handleStepChange = (current: number, target: number) => {
    if (target >= current) {
      return false;
    }

    setCurrentStepIndex(target);

    return true;
  };

  const availableStepIndexes = Array.from(
    { length: currentStepIndex + 1 },
    (_value, index) => index
  );

  const renderError = () => {
    const message = stepError || error;

    if (message === null || message === '') {
      return null;
    }

    return (
      <div ref={errorRef} tabIndex={-1} className="outline-none">
        <Alert variant={AlertVariant.DANGER}>{message}</Alert>
      </div>
    );
  };

  const renderDetails = () => {
    if (requestData.kind === RecurringObligationKind.BILL) {
      return (
        <div className="space-y-4">
          <Input
            id="recurring-bill-name"
            name="recurring_bill_name"
            type="text"
            label="Bill name"
            value={requestData.label}
            has_error={fieldErrors.label !== undefined}
            error={fieldErrors.label}
            onChange={(event) =>
              setRequestData({ ...requestData, label: event.target.value })
            }
          />
          <MoneyInput
            id="recurring-bill-amount"
            name="recurring_bill_amount"
            label="Recurring amount"
            value={requestData.amount_dollars}
            has_error={fieldErrors.amount_dollars !== undefined}
            error={fieldErrors.amount_dollars}
            on_value_change={(value) =>
              setRequestData({ ...requestData, amount_dollars: value })
            }
          />
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <Input
          id="recurring-debt-label"
          name="recurring_debt_label"
          type="text"
          label="Label"
          value={requestData.label}
          has_error={fieldErrors.label !== undefined}
          error={fieldErrors.label}
          onChange={(event) =>
            setRequestData({ ...requestData, label: event.target.value })
          }
        />
        <MoneyInput
          id="recurring-debt-balance"
          name="recurring_debt_balance"
          label="Current balance"
          value={requestData.current_balance_dollars}
          has_error={fieldErrors.current_balance_dollars !== undefined}
          error={fieldErrors.current_balance_dollars}
          on_value_change={(value) =>
            setRequestData({ ...requestData, current_balance_dollars: value })
          }
        />
        <MoneyInput
          id="recurring-debt-minimum"
          name="recurring_debt_minimum"
          label="Minimum payment"
          value={requestData.minimum_payment_dollars}
          has_error={fieldErrors.minimum_payment_dollars !== undefined}
          error={fieldErrors.minimum_payment_dollars}
          on_value_change={(value) =>
            setRequestData({ ...requestData, minimum_payment_dollars: value })
          }
        />
        <MoneyInput
          id="recurring-debt-current"
          name="recurring_debt_current"
          label="Current payment"
          value={requestData.current_payment_dollars}
          has_error={fieldErrors.current_payment_dollars !== undefined}
          error={fieldErrors.current_payment_dollars}
          on_value_change={(value) =>
            setRequestData({ ...requestData, current_payment_dollars: value })
          }
        />
      </div>
    );
  };

  const getAmount = () => {
    if (requestData.kind === RecurringObligationKind.BILL) {
      return requestData.amount_dollars;
    }

    return requestData.current_payment_dollars;
  };
  const effectiveImportant =
    requestData.is_required ||
    requestData.payment_schedule.auto_deducted === true;

  const renderReviewSpecific = () => {
    if (requestData.kind !== RecurringObligationKind.DEBT) {
      return null;
    }

    return (
      <>
        <dt>Current balance</dt>
        <dd>
          {formatCentsAsCurrency(
            dollarsToCents(requestData.current_balance_dollars)
          )}
        </dd>
        <dt>Minimum payment</dt>
        <dd>
          {formatCentsAsCurrency(
            dollarsToCents(requestData.minimum_payment_dollars)
          )}
        </dd>
      </>
    );
  };

  const renderConfiguration = () => {
    if (configuration === null) {
      return <p role="status">Loading payment schedule…</p>;
    }

    let importantValue = 'no';

    if (requestData.is_required) {
      importantValue = 'yes';
    }

    return (
      <div className="space-y-4">
        <Select
          id="important-payment"
          name="important_payment"
          label="Important payment"
          value={importantValue}
          has_error={false}
          onChange={(event) =>
            setRequestData({
              ...requestData,
              is_required: event.target.value === 'yes',
            })
          }
        >
          <option value="no">No</option>
          <option value="yes">Yes</option>
        </Select>
        <PaymentScheduleFields
          id="new-payment-schedule"
          label="this payment"
          representative_date={configuration.representative_date}
          pay_period_type={configuration.pay_period_type}
          schedule={requestData.payment_schedule}
          error={fieldErrors.payment_schedule}
          on_change={(paymentSchedule) =>
            setRequestData({
              ...requestData,
              payment_schedule: paymentSchedule,
            })
          }
        />
      </div>
    );
  };

  const renderFundingPaycheckReview = () => {
    if (
      requestData.payment_schedule.timing ===
      ExpensePaymentTiming.EVERY_PAYCHECK
    ) {
      return null;
    }

    return (
      <>
        <dt>Funding paycheck</dt>
        <dd>{requestData.payment_schedule.paycheck_position}</dd>
      </>
    );
  };

  const renderDateReview = () => {
    if (
      requestData.payment_schedule.timing !== ExpensePaymentTiming.DAY_OF_MONTH
    ) {
      return null;
    }

    let autoDeducted = 'No';

    if (requestData.payment_schedule.auto_deducted === true) {
      autoDeducted = 'Yes';
    }

    return (
      <>
        <dt>Date of month</dt>
        <dd>{requestData.payment_schedule.day_of_month}</dd>
        <dt>Auto deducted</dt>
        <dd>{autoDeducted}</dd>
      </>
    );
  };

  const getEffectiveImportantLabel = () => {
    if (effectiveImportant) {
      return 'Yes';
    }

    return 'No';
  };

  return (
    <div className="py-2">
      {renderError()}
      <FormWizard
        total_steps={4}
        name="Add a recurring payment"
        is_loading={loading}
        on_request_next={handleNext}
        on_request_step_change={handleStepChange}
        form_error={null}
        available_step_indexes={availableStepIndexes}
        render_card={false}
      >
        <Step step_title="Payment type">
          <div className="space-y-4">
            <p>What are you adding?</p>
            <p className="text-sm">
              This flow is for recurring payments. One-off spending is not
              tracked here yet.
            </p>
            <Select
              id="payment-kind"
              name="payment_kind"
              label="Payment type"
              value={requestData.kind}
              has_error={fieldErrors.kind !== undefined}
              error={fieldErrors.kind}
              onChange={updateKind}
            >
              <option value="">Select a type</option>
              <option value={RecurringObligationKind.BILL}>Bill</option>
              <option value={RecurringObligationKind.DEBT}>Debt</option>
            </Select>
          </div>
        </Step>
        <Step step_title="Details">{renderDetails()}</Step>
        <Step step_title="Budgeting and payment schedule">
          {renderConfiguration()}
        </Step>
        <Step step_title="Review">
          <dl className="grid grid-cols-2 gap-3">
            <dt>Type</dt>
            <dd>{requestData.kind}</dd>
            <dt>Name</dt>
            <dd>{requestData.label}</dd>
            {renderReviewSpecific()}
            <dt>Payment</dt>
            <dd>{formatCentsAsCurrency(dollarsToCents(getAmount()))}</dd>
            <dt>Effective Important</dt>
            <dd>{getEffectiveImportantLabel()}</dd>
            <dt>Schedule</dt>
            <dd>{requestData.payment_schedule.timing}</dd>
            {renderFundingPaycheckReview()}
            {renderDateReview()}
          </dl>
        </Step>
      </FormWizard>
    </div>
  );
};

export default AddBillSidePeek;
