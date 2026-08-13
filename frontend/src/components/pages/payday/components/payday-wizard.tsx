import { useMemo, useRef } from 'react';

import PaydayDebtBalanceStep from './payday-debt-balance-step';
import PaydayLineItemStep from './payday-line-item-step';
import PaydayPayChequeStep from './payday-pay-cheque-step';
import PaydaySummaryStep from './payday-summary-step';
import PaydayWarnings from './payday-warnings';
import PaydayWizardProps from './types/payday-wizard-props';

import { usePaydayQueueContext } from 'components/pages/payday/context/use-payday-queue-context';
import { usePaydayBacklogProgression } from 'components/pages/payday/hooks/use-payday-backlog-progression';
import { usePaydayWizardPersistence } from 'components/pages/payday/hooks/use-payday-wizard-persistence';
import { getPaydayResumeIndex } from 'components/pages/payday/utils/payday-wizard-state';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import FormWizard from 'ui/form-wizard/form-wizard';
import Step from 'ui/form-wizard/step';

import { useFocusRequest } from 'util/hooks/use-focus-request';

const PaydayWizard = ({
  detail,
  period_id,
  refresh_detail,
}: PaydayWizardProps) => {
  const errorRef = useRef<HTMLDivElement>(null);
  const { queue } = usePaydayQueueContext();
  const { request_focus: requestStepErrorFocus } = useFocusRequest({
    target_ref: errorRef,
  });
  const lineItems = useMemo(
    () =>
      [...detail.pay_period.line_items].sort((leftLineItem, rightLineItem) => {
        const orderDifference =
          leftLineItem.display_order - rightLineItem.display_order;

        if (orderDifference !== 0) {
          return orderDifference;
        }

        return leftLineItem.id - rightLineItem.id;
      }),
    [detail.pay_period.line_items]
  );
  const stepIndexes = useMemo(() => {
    const firstLineItem = 1;
    const firstDebtBalance = firstLineItem + lineItems.length;
    const summary = firstDebtBalance + detail.debt_balance_checks.length;

    return {
      first_line_item: firstLineItem,
      first_debt_balance: firstDebtBalance,
      summary,
      total: summary + 1,
    };
  }, [detail.debt_balance_checks.length, lineItems.length]);
  const initialIndex = useMemo(
    () =>
      getPaydayResumeIndex(
        detail.pay_period,
        lineItems,
        detail.debt_balance_checks
      ),
    [detail.debt_balance_checks, detail.pay_period, lineItems]
  );
  const availableStepIndexes = useMemo(
    () =>
      Array.from({ length: initialIndex + 1 }, (_unusedValue, index) => index),
    [initialIndex]
  );
  const { is_caught_up, finish_payday } =
    usePaydayBacklogProgression(period_id);
  const {
    warnings,
    displayed_error,
    pay_cheque_errors,
    line_item_errors,
    debt_balance_errors,
    pay_cheque_mutation,
    line_item_mutation,
    debt_balance_mutation,
    is_loading,
    requested_step_index,
    persist_step,
    handle_step_change,
  } = usePaydayWizardPersistence({
    detail,
    period_id,
    line_items: lineItems,
    debt_balance_checks: detail.debt_balance_checks,
    first_line_item_step_index: stepIndexes.first_line_item,
    first_debt_balance_step_index: stepIndexes.first_debt_balance,
    summary_step_index: stepIndexes.summary,
    refresh_detail,
    finish_payday,
    focus_step_error: requestStepErrorFocus,
  });

  const effectiveDate = queue?.effective_date ?? detail.pay_period.pay_date;
  const isHistorical = detail.pay_period.pay_date < effectiveDate;

  const renderStepError = () => {
    if (displayed_error === null) {
      return null;
    }

    return (
      <div ref={errorRef} tabIndex={-1}>
        <Alert variant={AlertVariant.DANGER}>{displayed_error}</Alert>
      </div>
    );
  };

  const renderLineItemSteps = () => {
    return lineItems.map((lineItem) => (
      <Step key={lineItem.id} step_title={lineItem.title}>
        <PaydayLineItemStep
          line_item={lineItem}
          request={line_item_mutation.request}
          set_request={line_item_mutation.set_request}
          field_errors={line_item_errors}
          allow_unknown={isHistorical}
          disabled={is_loading}
        />
      </Step>
    ));
  };

  const renderCaughtUp = () => {
    if (!is_caught_up) {
      return null;
    }

    return <Alert variant={AlertVariant.SUCCESS}>You&apos;re caught up.</Alert>;
  };

  const renderDebtBalanceSteps = () => {
    return detail.debt_balance_checks.map((balanceCheck) => (
      <Step
        key={balanceCheck.source_key}
        step_title={`${balanceCheck.title} balance`}
      >
        <PaydayDebtBalanceStep
          balance_check={balanceCheck}
          request={debt_balance_mutation.request}
          set_request={debt_balance_mutation.set_request}
          field_errors={debt_balance_errors}
          allow_unknown={isHistorical}
          disabled={is_loading}
        />
      </Step>
    ));
  };

  return (
    <div className="space-y-4">
      {renderStepError()}
      {renderCaughtUp()}
      <PaydayWarnings warnings={warnings} />
      <FormWizard
        key={period_id}
        total_steps={stepIndexes.total}
        initial_index={initialIndex}
        requested_index={requested_step_index}
        name="Payday reconciliation"
        render_card={false}
        is_loading={is_loading}
        form_error={null}
        available_step_indexes={availableStepIndexes}
        on_request_next={persist_step}
        on_request_step_change={handle_step_change}
        render_loading_icon={() => (
          <i
            className="fa-solid fa-arrows-rotate animate-spin"
            aria-hidden="true"
          />
        )}
      >
        <Step step_title="Pay cheque">
          <PaydayPayChequeStep
            planned_amount_cents={detail.pay_period.pay_cheque_cents}
            request={pay_cheque_mutation.request}
            set_request={pay_cheque_mutation.set_request}
            field_errors={pay_cheque_errors}
            allow_unknown={isHistorical}
            disabled={is_loading}
          />
        </Step>
        {renderLineItemSteps()}
        {renderDebtBalanceSteps()}
        <Step step_title="Summary">
          <PaydaySummaryStep detail={detail} warnings={warnings} />
        </Step>
      </FormWizard>
    </div>
  );
};

export default PaydayWizard;
