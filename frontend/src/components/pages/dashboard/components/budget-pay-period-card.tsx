import clsx from 'clsx';
import { motion, useReducedMotion } from 'motion/react';
import React, { type MouseEvent, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';

import BudgetCardEditor from './budget-card-editor';
import BudgetPayPeriodCardProps from './types/budget-pay-period-card-props';

import {
  calculateFinancialVariance,
  formatCentsAsCurrency,
  formatFinancialVariance,
} from 'lib/money/money';

import { BudgetLineItemDefinition } from 'components/pages/dashboard/api/hooks/definitions/budget-line-item-definition';
import {
  DebtBalanceReviewStatus,
  PayChequeReviewStatus,
  PaydayReconciliationStatus,
  PaymentReviewStatus,
} from 'components/pages/payday/enums/payday-status';
import { PaymentCompletionStatus } from 'components/pages/payday/enums/payment-completion-status';

import { getPaydayRoute } from 'router/utils/get-payday-route';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import Card from 'ui/cards/card';

const BudgetPayPeriodCard = ({
  period,
  line_items,
  on_saved,
  on_pay_date_saved,
  effective_payday_date,
  register_focus_target,
}: BudgetPayPeriodCardProps) => {
  const shouldReduceMotion = useReducedMotion();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const editButtonRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const hasEnteredEditingRef = useRef(false);

  useEffect(() => {
    if (isEditing) {
      hasEnteredEditingRef.current = true;
      closeButtonRef.current?.focus();

      return;
    }

    if (hasEnteredEditingRef.current) {
      editButtonRef.current?.focus();
    }
  }, [isEditing]);

  const isReducedMotion = shouldReduceMotion === true;
  const isPaydayEligible =
    effective_payday_date !== null && period.pay_date <= effective_payday_date;
  const hasFinancialDanger =
    period.has_negative_left_over ||
    period.affects_important_expenses ||
    period.has_missed_important_expenses;

  const handleEditButtonRef = (element: HTMLButtonElement | null) => {
    editButtonRef.current = element;

    if (!isPaydayEligible) {
      register_focus_target?.(element);
    }
  };

  const handleStartEditing = () => {
    setIsEditing(true);
  };

  const handleEditClick = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    handleStartEditing();
  };

  const handlePaydayClick = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    void navigate(getPaydayRoute(period.id));
  };

  const formatPayDate = (isoDate: string): string => {
    const [year, month, day] = isoDate.split('-');

    return `${month}-${day}-${year}`;
  };

  const formatAccessiblePayDate = (isoDate: string): string => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC',
    }).format(new Date(`${isoDate}T00:00:00Z`));
  };

  const renderAlert = () => {
    const hasAlert =
      period.has_negative_left_over ||
      period.affects_important_expenses ||
      period.has_missed_important_expenses ||
      period.is_below_warning_threshold ||
      period.has_deferred_items;

    if (!hasAlert) {
      return null;
    }

    if (period.has_negative_left_over) {
      return (
        <Alert variant={AlertVariant.DANGER}>
          Your bills are more than you are making for this pay period.
        </Alert>
      );
    }

    if (period.affects_important_expenses) {
      return (
        <Alert variant={AlertVariant.DANGER}>
          An important bill may be affected on this pay period.
        </Alert>
      );
    }

    if (period.has_missed_important_expenses) {
      return (
        <Alert variant={AlertVariant.DANGER}>
          An Important payment was missed or underpaid on this pay period.
        </Alert>
      );
    }

    return (
      <Alert variant={AlertVariant.WARNING}>
        Review the warning conditions for this pay period.
      </Alert>
    );
  };

  const renderReconciliationStatus = () => {
    if (!isPaydayEligible) {
      return null;
    }

    if (
      period.payday_reconciliation_status ===
      PaydayReconciliationStatus.INCOMPLETE
    ) {
      return (
        <span className="bg-storm-dust-200 text-storm-dust-800 dark:bg-storm-dust-700 dark:text-storm-dust-100 inline-flex rounded-full px-2 py-1 text-xs font-bold">
          Incomplete history
        </span>
      );
    }

    if (
      period.payday_reconciliation_status ===
      PaydayReconciliationStatus.IN_PROGRESS
    ) {
      return (
        <span className="bg-sweet-corn-100 text-sweet-corn-900 dark:bg-sweet-corn-900 dark:text-sweet-corn-100 inline-flex rounded-full px-2 py-1 text-xs font-bold">
          Payday review in progress
        </span>
      );
    }

    if (
      period.payday_reconciliation_status ===
      PaydayReconciliationStatus.NOT_STARTED
    ) {
      return (
        <span className="bg-blue-bell-100 text-blue-bell-900 dark:bg-blue-bell-900 dark:text-blue-bell-100 inline-flex rounded-full px-2 py-1 text-xs font-bold">
          Needs payday review
        </span>
      );
    }

    const getCompletionClassName = () => {
      if (period.payment_completion_status === PaymentCompletionStatus.GREEN) {
        return 'bg-tom-thumb-100 text-tom-thumb-900 dark:bg-tom-thumb-900 dark:text-tom-thumb-100';
      }

      if (period.payment_completion_status === PaymentCompletionStatus.YELLOW) {
        return 'bg-sweet-corn-100 text-sweet-corn-900 dark:bg-sweet-corn-900 dark:text-sweet-corn-100';
      }

      return 'bg-persian-plum-100 text-persian-plum-900 dark:bg-persian-plum-900 dark:text-persian-plum-100';
    };

    const renderCompletionText = () => {
      if (
        period.payment_completion_status === PaymentCompletionStatus.NO_BILLS
      ) {
        return 'No bills due · Review complete';
      }

      return `${period.paid_bill_count} paid · ${period.scheduled_bill_count} scheduled · ${period.missed_bill_count} missed`;
    };

    return (
      <span
        className={clsx(
          'inline-flex rounded-full px-2 py-1 text-xs font-bold',
          getCompletionClassName()
        )}
      >
        {renderCompletionText()}
      </span>
    );
  };

  const renderPaydayAction = () => {
    if (!isPaydayEligible) {
      return null;
    }

    const getLabel = () => {
      if (
        period.payday_reconciliation_status ===
        PaydayReconciliationStatus.NOT_STARTED
      ) {
        return 'Start payday review';
      }

      if (
        period.payday_reconciliation_status ===
        PaydayReconciliationStatus.IN_PROGRESS
      ) {
        return 'Continue payday review';
      }

      return 'Review payday';
    };

    const label = getLabel();

    return (
      <IconButton
        icon="fa-solid fa-list-check"
        label={label}
        show_label
        variant={ButtonVariant.WARNING}
        on_click={handlePaydayClick}
        additional_css="w-full justify-center"
        button_ref={register_focus_target}
      />
    );
  };

  const renderActualPayCheque = () => {
    if (period.pay_cheque_review_status === PayChequeReviewStatus.UNKNOWN) {
      return (
        <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
          Actual pay cheque unknown
        </span>
      );
    }

    if (
      period.pay_cheque_review_status !== PayChequeReviewStatus.CONFIRMED ||
      period.actual_pay_cheque_cents === null
    ) {
      return null;
    }

    const variance = calculateFinancialVariance(
      period.pay_cheque_cents,
      period.actual_pay_cheque_cents
    );

    return (
      <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
        Actual {formatCentsAsCurrency(period.actual_pay_cheque_cents)} ·{' '}
        {formatFinancialVariance(variance)}
      </span>
    );
  };

  const renderActualLineItem = (
    currentEntry: BudgetLineItemDefinition | undefined
  ) => {
    if (currentEntry === undefined) {
      return null;
    }

    if (currentEntry.payment_review_status === PaymentReviewStatus.NOT_PAID) {
      return (
        <span className="text-persian-plum-700 dark:text-persian-plum-300 block text-xs font-semibold">
          Not paid
        </span>
      );
    }

    if (currentEntry.payment_review_status === PaymentReviewStatus.UNKNOWN) {
      return (
        <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
          Unknown
        </span>
      );
    }

    if (currentEntry.payment_review_status === PaymentReviewStatus.SCHEDULED) {
      const expectedAmount = currentEntry.scheduled_amount_cents;
      const expectedDate = currentEntry.expected_payment_date;

      if (expectedAmount === null || expectedDate === null) {
        return null;
      }

      const variance = calculateFinancialVariance(
        currentEntry.amount_cents,
        expectedAmount
      );

      return (
        <span className="text-blue-bell-700 dark:text-blue-bell-300 block text-xs font-semibold">
          Scheduled for {formatPayDate(expectedDate)} ·{' '}
          {formatCentsAsCurrency(expectedAmount)} expected ·{' '}
          {formatFinancialVariance(variance)}
        </span>
      );
    }

    if (
      currentEntry.payment_review_status !== PaymentReviewStatus.PAID ||
      currentEntry.actual_amount_cents === null
    ) {
      return null;
    }

    const variance = calculateFinancialVariance(
      currentEntry.amount_cents,
      currentEntry.actual_amount_cents
    );

    return (
      <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
        Actual {formatCentsAsCurrency(currentEntry.actual_amount_cents)} ·{' '}
        {formatFinancialVariance(variance)} · Paid
      </span>
    );
  };

  const getCardClassName = () => {
    if (hasFinancialDanger) {
      return 'group relative h-full border-2 border-persian-plum-600 transition hover:shadow-md dark:border-persian-plum-400';
    }

    if (
      !isPaydayEligible ||
      period.payday_reconciliation_status !==
        PaydayReconciliationStatus.REVIEWED
    ) {
      return 'group relative h-full transition hover:shadow-md';
    }

    if (
      period.payment_completion_status === PaymentCompletionStatus.GREEN ||
      period.payment_completion_status === PaymentCompletionStatus.NO_BILLS
    ) {
      return 'group relative h-full border-2 border-tom-thumb-600 transition hover:shadow-md dark:border-tom-thumb-400';
    }

    if (period.payment_completion_status === PaymentCompletionStatus.YELLOW) {
      return 'group relative h-full border-2 border-sweet-corn-500 transition hover:shadow-md dark:border-sweet-corn-400';
    }

    return 'group relative h-full border-2 border-persian-plum-600 transition hover:shadow-md dark:border-persian-plum-400';
  };

  const renderImportant = (lineItem: BudgetLineItemDefinition) => {
    if (!lineItem.is_required && !lineItem.is_auto_deducted) {
      return null;
    }

    const renderImportantBadge = () => {
      if (!lineItem.is_required) {
        return null;
      }

      return (
        <span className="bg-sweet-corn-100 text-sweet-corn-900 dark:bg-sweet-corn-900 dark:text-sweet-corn-100 inline-flex rounded-full px-2 py-0.5 text-xs font-bold">
          <i
            className="fa-solid fa-circle-exclamation mr-1"
            aria-hidden="true"
          />
          Important
        </span>
      );
    };

    const renderAutoDeductedBadge = () => {
      if (!lineItem.is_auto_deducted) {
        return null;
      }

      return (
        <span className="bg-blue-bell-100 text-blue-bell-900 dark:bg-blue-bell-900 dark:text-blue-bell-100 inline-flex rounded-full px-2 py-0.5 text-xs font-bold">
          Auto-deducted
        </span>
      );
    };

    return (
      <span className="flex flex-wrap gap-1">
        {renderImportantBadge()}
        {renderAutoDeductedBadge()}
      </span>
    );
  };

  const renderDebtBalances = () => {
    if (period.debt_balance_checks.length === 0) {
      return null;
    }

    return period.debt_balance_checks.map((balanceCheck) => {
      const renderBalanceComparison = () => {
        if (balanceCheck.review_status === DebtBalanceReviewStatus.UNKNOWN) {
          return (
            <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
              Actual balance unknown
            </span>
          );
        }

        if (balanceCheck.expected_balance_cents === null) {
          return (
            <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
              Expected balance unavailable
            </span>
          );
        }

        if (balanceCheck.actual_balance_cents === null) {
          return null;
        }

        const variance = calculateFinancialVariance(
          balanceCheck.expected_balance_cents,
          balanceCheck.actual_balance_cents
        );

        return (
          <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
            Actual {formatCentsAsCurrency(balanceCheck.actual_balance_cents)} ·{' '}
            {formatFinancialVariance(variance)}
          </span>
        );
      };

      const getExpectedBalanceText = () => {
        if (balanceCheck.expected_balance_cents === null) {
          return 'Expected unavailable';
        }

        return formatCentsAsCurrency(balanceCheck.expected_balance_cents);
      };

      const renderBalanceMovement = () => {
        const movement = balanceCheck.movement_from_previous_percentage;

        if (movement === null) {
          return null;
        }

        let direction = 'down';

        if (movement >= 0) {
          direction = 'up';
        }

        return (
          <span className="text-storm-dust-500 dark:text-storm-dust-400 block text-xs">
            Balance {direction} {Math.abs(movement).toFixed(1)}% since last
            confirmed
          </span>
        );
      };

      return (
        <React.Fragment key={balanceCheck.source_key}>
          <dt className="text-storm-dust-500 dark:text-storm-dust-400">
            {balanceCheck.title} balance
          </dt>
          <dd className="text-right">
            {getExpectedBalanceText()}
            {renderBalanceComparison()}
            {renderBalanceMovement()}
          </dd>
        </React.Fragment>
      );
    });
  };

  const getLeftOverClassName = () => {
    return clsx(
      'border-blue-bell-300 dark:border-blue-bell-700 mt-2 border-t pt-4 text-right text-xl font-extrabold',
      {
        'text-persian-plum-700 dark:text-persian-plum-300':
          period.left_over_cents < 0,
        'text-tom-thumb-700 dark:text-tom-thumb-300':
          period.left_over_cents >= 0,
      }
    );
  };

  const renderShortfall = (
    currentEntry: BudgetLineItemDefinition | undefined
  ) => {
    if (currentEntry === undefined || currentEntry.shortfall_cents <= 0) {
      return null;
    }

    return (
      <span className="text-persian-plum-700 dark:text-persian-plum-300 block text-xs font-bold">
        Short {formatCentsAsCurrency(currentEntry.shortfall_cents)}
      </span>
    );
  };

  const getLineItemAmountClassName = (
    currentEntry: BudgetLineItemDefinition | undefined
  ) => {
    if (currentEntry !== undefined && currentEntry.shortfall_cents > 0) {
      return 'text-persian-plum-700 dark:text-persian-plum-300 text-right font-bold';
    }

    return 'text-right font-medium';
  };

  const renderFront = () => {
    const currentEntries = new Map(
      period.line_items.map((lineItem) => [lineItem.source_key, lineItem])
    );

    const renderLineItems = () => {
      return line_items.map((lineItem) => {
        const currentEntry = currentEntries.get(lineItem.source_key);
        let amountCents = 0;

        if (currentEntry !== undefined) {
          amountCents = currentEntry.amount_cents;
        }

        return (
          <React.Fragment key={lineItem.source_key}>
            <dt className="text-storm-dust-700 dark:text-storm-dust-300 flex min-w-0 flex-col gap-1">
              <span className="truncate">{lineItem.title}</span>
              {renderImportant(lineItem)}
            </dt>
            <dd className={getLineItemAmountClassName(currentEntry)}>
              {formatCentsAsCurrency(amountCents)}
              {renderShortfall(currentEntry)}
              {renderActualLineItem(currentEntry)}
            </dd>
          </React.Fragment>
        );
      });
    };

    return (
      <Card additional_css={getCardClassName()}>
        {/* The pencil is the native keyboard action; this surface is pointer-only to avoid nested button semantics. */}
        {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */}
        <div className="space-y-4" onClick={handleStartEditing}>
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-storm-dust-900 dark:text-storm-dust-50 min-w-0 font-semibold">
              Pay Period: {formatPayDate(period.pay_date)}
            </h2>
            <IconButton
              icon="fa-solid fa-pencil"
              label={`Edit budget for ${formatAccessiblePayDate(period.pay_date)}`}
              variant={ButtonVariant.GHOST}
              on_click={handleEditClick}
              button_ref={handleEditButtonRef}
              additional_css="relative z-20 shrink-0 rounded-full text-blue-bell-700 pointer-events-auto dark:text-blue-bell-300"
            />
          </div>
          {renderAlert()}
          <div className="flex flex-wrap gap-2">
            {renderReconciliationStatus()}
          </div>
          <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
            <dt className="text-storm-dust-500 dark:text-storm-dust-400">
              Pay cheque
            </dt>
            <dd className="text-right">
              {formatCentsAsCurrency(period.pay_cheque_cents)}
              {renderActualPayCheque()}
            </dd>
            <dt className="text-storm-dust-500 dark:text-storm-dust-400">
              Previous period left over
            </dt>
            <dd className="text-right">
              {formatCentsAsCurrency(period.carried_left_over_cents)}
            </dd>
            <dt className="text-storm-dust-500 dark:text-storm-dust-400">
              Your total
            </dt>
            <dd className="text-right">
              {formatCentsAsCurrency(period.total_available_cents)}
            </dd>
            {renderLineItems()}
            {renderDebtBalances()}
            <dt className="border-storm-dust-200 dark:border-storm-dust-700 border-t pt-3 font-medium">
              Total bills
            </dt>
            <dd className="border-storm-dust-200 dark:border-storm-dust-700 border-t pt-3 text-right font-medium">
              {formatCentsAsCurrency(period.total_bills_cents)}
            </dd>
            <dt className="border-blue-bell-300 dark:border-blue-bell-700 mt-2 border-t pt-4 text-lg font-extrabold">
              Left over
            </dt>
            <dd className={getLeftOverClassName()}>
              {formatCentsAsCurrency(period.left_over_cents)}
            </dd>
          </dl>
          <div>{renderPaydayAction()}</div>
        </div>
      </Card>
    );
  };

  const renderBack = () => {
    return (
      <Card
        additional_css="h-full overflow-hidden"
        content_css="h-full overflow-y-auto overscroll-contain"
      >
        <BudgetCardEditor
          period={period}
          line_items={line_items}
          on_close={() => setIsEditing(false)}
          on_saved={on_saved}
          on_pay_date_saved={on_pay_date_saved}
          close_button_ref={closeButtonRef}
        />
      </Card>
    );
  };

  const getShellAnimation = () => {
    if (isEditing && !isReducedMotion) {
      return { rotateY: 180 };
    }

    return { rotateY: 0 };
  };

  const getShellTransition = () => {
    if (isReducedMotion) {
      return { duration: 0 };
    }

    return { duration: 0.35 };
  };

  const getFrontInert = () => {
    if (!isEditing) {
      return undefined;
    }

    return true;
  };

  const getBackInert = () => {
    if (isEditing) {
      return undefined;
    }

    return true;
  };

  return (
    <article className="h-full [perspective:1200px]">
      <motion.div
        animate={getShellAnimation()}
        transition={getShellTransition()}
        className="relative h-full [transform-style:preserve-3d]"
      >
        <div
          aria-hidden={isEditing}
          inert={getFrontInert()}
          className={clsx('relative h-full [backface-visibility:hidden]', {
            'z-10': !isEditing,
            'z-0': isEditing,
            'pointer-events-auto': !isEditing,
            'pointer-events-none': isEditing,
            invisible: isReducedMotion && isEditing,
          })}
        >
          {renderFront()}
        </div>
        <div
          aria-hidden={!isEditing}
          inert={getBackInert()}
          className={clsx(
            'absolute inset-0 h-full [transform:rotateY(180deg)] [backface-visibility:hidden]',
            {
              'z-0': !isEditing,
              'z-10': isEditing,
              'pointer-events-none': !isEditing,
              'pointer-events-auto': isEditing,
              '[transform:none]': isReducedMotion,
              invisible: isReducedMotion && !isEditing,
            }
          )}
        >
          {renderBack()}
        </div>
      </motion.div>
    </article>
  );
};

export default BudgetPayPeriodCard;
