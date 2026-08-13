import { useState } from 'react';

import UsePaydayWizardPersistenceDefinition from './definitions/use-payday-wizard-persistence-definition';
import UsePaydayWizardPersistenceParamsDefinition from './definitions/use-payday-wizard-persistence-params-definition';

import { useEventSystem } from 'lib/event-system/hooks/use-event-system';

import PaydayMutationResponseDefinition from 'components/pages/payday/api/hooks/definitions/payday-mutation-response-definition';
import PaydayWarningDefinition from 'components/pages/payday/api/hooks/definitions/payday-warning-definition';
import { useUpdatePaydayDebtBalance } from 'components/pages/payday/api/hooks/use-update-payday-debt-balance';
import { useUpdatePaydayLineItem } from 'components/pages/payday/api/hooks/use-update-payday-line-item';
import { useUpdatePaydayPayCheque } from 'components/pages/payday/api/hooks/use-update-payday-pay-cheque';
import { PAY_CHEQUE_STEP_INDEX } from 'components/pages/payday/constants/pay-cheque-step-index';
import { usePaydayQueueContext } from 'components/pages/payday/context/use-payday-queue-context';
import { PaydayReconciliationStatus } from 'components/pages/payday/enums/payday-status';
import BudgetPeriodsRecalculatedEventPayload from 'components/pages/payday/events/definitions/budget-periods-recalculated-event-payload';
import { PaydayEvent } from 'components/pages/payday/events/payday-event';
import { PaydayEventEmitterName } from 'components/pages/payday/events/payday-event-emitter-name';
import { PaydayEventMap } from 'components/pages/payday/events/payday-event-map';
import {
  buildInitialDebtBalanceRequest,
  buildInitialLineItemRequest,
  buildInitialPayChequeRequest,
  getPaydayResumeIndex,
} from 'components/pages/payday/utils/payday-wizard-state';
import PaydayDebtBalanceFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-debt-balance-field-errors-definition';
import PaydayLineItemFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-line-item-field-errors-definition';
import PaydayPayChequeFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-pay-cheque-field-errors-definition';
import { usePaydayFormValidation } from 'components/pages/payday/validations/hooks/use-payday-form-validation';

export const usePaydayWizardPersistence = ({
  detail,
  period_id,
  line_items,
  debt_balance_checks,
  first_line_item_step_index,
  first_debt_balance_step_index,
  summary_step_index,
  refresh_detail,
  finish_payday,
  focus_step_error,
}: UsePaydayWizardPersistenceParamsDefinition): UsePaydayWizardPersistenceDefinition => {
  const { refresh: refreshQueue } = usePaydayQueueContext();
  const eventSystem = useEventSystem();
  const [warnings, setWarnings] = useState<PaydayWarningDefinition[]>([]);
  const [stepError, setStepError] = useState<string | null>(null);
  const [requestedStepIndex, setRequestedStepIndex] = useState<number>();
  const [payChequeErrors, setPayChequeErrors] =
    useState<PaydayPayChequeFieldErrorsDefinition>({});
  const [lineItemErrors, setLineItemErrors] =
    useState<PaydayLineItemFieldErrorsDefinition>({});
  const [debtBalanceErrors, setDebtBalanceErrors] =
    useState<PaydayDebtBalanceFieldErrorsDefinition>({});
  const payChequeMutation = useUpdatePaydayPayCheque({
    period_id,
    initial_request: buildInitialPayChequeRequest(detail.pay_period),
  });
  const lineItemMutation = useUpdatePaydayLineItem({
    period_id,
    initial_request: buildInitialLineItemRequest(line_items),
  });
  const debtBalanceMutation = useUpdatePaydayDebtBalance({
    period_id,
    initial_request: buildInitialDebtBalanceRequest(debt_balance_checks),
  });
  const {
    validatePayChequeStep,
    validateLineItemStep,
    validateDebtBalanceStep,
  } = usePaydayFormValidation();

  const isLoading =
    payChequeMutation.loading ||
    lineItemMutation.loading ||
    debtBalanceMutation.loading;
  const displayedError =
    stepError ??
    payChequeMutation.error ??
    lineItemMutation.error ??
    debtBalanceMutation.error;

  const clearErrors = () => {
    setStepError(null);
    setPayChequeErrors({});
    setLineItemErrors({});
    setDebtBalanceErrors({});
  };

  const refreshAfterMutation = async (
    response: PaydayMutationResponseDefinition
  ) => {
    setWarnings(response.warnings);

    await refresh_detail();
    await refreshQueue();
    const emitter = eventSystem.fetchOrCreateEventEmitter<PaydayEventMap>(
      PaydayEventEmitterName.PAYDAY
    );
    const payload: BudgetPeriodsRecalculatedEventPayload = {
      source_pay_period_id: period_id,
      affected_pay_period_ids: response.affected_pay_period_ids,
    };
    emitter.emit(PaydayEvent.BUDGET_PERIODS_RECALCULATED, payload);
  };

  const hydrateStepRequest = (targetIndex: number) => {
    if (targetIndex === PAY_CHEQUE_STEP_INDEX) {
      payChequeMutation.set_request(
        buildInitialPayChequeRequest(detail.pay_period)
      );

      return;
    }

    const lineItemIndex = targetIndex - first_line_item_step_index;
    const lineItem = line_items[lineItemIndex];

    if (lineItem !== undefined) {
      lineItemMutation.set_request({
        review_status: lineItem.payment_review_status,
        actual_amount_cents: lineItem.actual_amount_cents,
        scheduled_amount_cents: lineItem.scheduled_amount_cents,
      });

      return;
    }

    const debtBalanceIndex = targetIndex - first_debt_balance_step_index;
    const debtBalance = debt_balance_checks[debtBalanceIndex];

    if (debtBalance === undefined) {
      return;
    }

    debtBalanceMutation.set_request({
      source_key: debtBalance.source_key,
      title: debtBalance.title,
      review_status: debtBalance.review_status,
      actual_balance_cents: debtBalance.actual_balance_cents,
    });
  };

  const persistStep = async (currentIndex: number) => {
    clearErrors();

    if (currentIndex === summary_step_index) {
      const refreshedDetail = await refresh_detail();

      if (
        refreshedDetail === null ||
        ![
          PaydayReconciliationStatus.REVIEWED,
          PaydayReconciliationStatus.INCOMPLETE,
        ].includes(refreshedDetail.progress.overall_reconciliation_status)
      ) {
        setStepError('This payday still has items that need your attention.');

        if (refreshedDetail !== null) {
          setRequestedStepIndex(
            getPaydayResumeIndex(
              refreshedDetail.pay_period,
              refreshedDetail.pay_period.line_items,
              refreshedDetail.debt_balance_checks
            )
          );
        }

        focus_step_error();

        return false;
      }

      return finish_payday();
    }

    if (currentIndex === PAY_CHEQUE_STEP_INDEX) {
      const validationResult = validatePayChequeStep(payChequeMutation.request);

      if (!validationResult.is_valid) {
        setStepError(validationResult.step_error);
        setPayChequeErrors(validationResult.field_errors);
        focus_step_error();

        return false;
      }

      const response = await payChequeMutation.update_pay_cheque();

      if (response === null) {
        return false;
      }

      await refreshAfterMutation(response);
      hydrateStepRequest(currentIndex + 1);

      return true;
    }

    const lineItemIndex = currentIndex - first_line_item_step_index;
    const lineItem = line_items[lineItemIndex];

    if (lineItem !== undefined) {
      const validationResult = validateLineItemStep(lineItemMutation.request);

      if (!validationResult.is_valid) {
        setStepError(validationResult.step_error);
        setLineItemErrors(validationResult.field_errors);
        focus_step_error();

        return false;
      }

      const response = await lineItemMutation.update_line_item(lineItem.id);

      if (response === null) {
        return false;
      }

      await refreshAfterMutation(response);
      hydrateStepRequest(currentIndex + 1);

      return true;
    }

    const debtBalanceIndex = currentIndex - first_debt_balance_step_index;
    const debtBalance = debt_balance_checks[debtBalanceIndex];

    if (debtBalance === undefined) {
      return false;
    }

    const validationResult = validateDebtBalanceStep(
      debtBalanceMutation.request
    );

    if (!validationResult.is_valid) {
      setStepError(validationResult.step_error);
      setDebtBalanceErrors(validationResult.field_errors);
      focus_step_error();

      return false;
    }

    const response = await debtBalanceMutation.update_debt_balance();

    if (response === null) {
      return false;
    }

    await refreshAfterMutation(response);
    hydrateStepRequest(currentIndex + 1);

    return true;
  };

  const handleStepChange = async (
    currentIndex: number,
    targetIndex: number
  ) => {
    if (targetIndex < currentIndex) {
      clearErrors();
      hydrateStepRequest(targetIndex);

      return true;
    }

    const saved = await persistStep(currentIndex);

    if (!saved) {
      return false;
    }

    hydrateStepRequest(targetIndex);

    return true;
  };

  return {
    warnings,
    displayed_error: displayedError,
    pay_cheque_errors: payChequeErrors,
    line_item_errors: lineItemErrors,
    debt_balance_errors: debtBalanceErrors,
    pay_cheque_mutation: payChequeMutation,
    line_item_mutation: lineItemMutation,
    debt_balance_mutation: debtBalanceMutation,
    is_loading: isLoading,
    requested_step_index: requestedStepIndex,
    persist_step: persistStep,
    handle_step_change: handleStepChange,
  };
};
