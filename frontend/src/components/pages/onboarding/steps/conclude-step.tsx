import React from 'react';

import { dollarsToCents, formatCentsAsCurrency } from 'lib/money/money';

import { UtilityType } from 'components/pages/onboarding/enums/utility-type';
import ConcludeStepProps from 'components/pages/onboarding/types/conclude-step-props';
import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';
import { PaymentScheduleFormState } from 'components/payment-schedule/types/payment-schedule-form-state';

const ConcludeStep = ({
  debts,
  expenses,
  income,
  important_expenses,
}: ConcludeStepProps) => {
  const hasPositiveAmount = (amount: string) => {
    if (amount.trim() === '') {
      return false;
    }

    return dollarsToCents(amount) > 0;
  };

  const getScheduleDescription = (schedule: PaymentScheduleFormState) => {
    if (schedule.timing === ExpensePaymentTiming.EVERY_PAYCHECK) {
      return 'Every paycheck';
    }

    if (schedule.timing === ExpensePaymentTiming.DAY_OF_MONTH) {
      return `Monthly on day ${schedule.day_of_month}`;
    }

    if (schedule.paycheck_position === PaycheckPosition.SECOND) {
      return 'Second paycheck';
    }

    if (schedule.paycheck_position === PaycheckPosition.THIRD) {
      return 'Third paycheck';
    }

    if (schedule.paycheck_position === PaycheckPosition.FOURTH) {
      return 'Fourth paycheck';
    }

    if (schedule.paycheck_position === PaycheckPosition.LAST) {
      return 'Last paycheck';
    }

    return 'First paycheck';
  };

  const renderScheduleBadges = (
    sourceKey: string,
    schedule: PaymentScheduleFormState
  ) => {
    const isImportant =
      sourceKey === 'rent_or_mortgage' ||
      schedule.auto_deducted === true ||
      important_expenses.selected_keys.includes(sourceKey);

    if (!schedule.auto_deducted && !isImportant) {
      return null;
    }

    const renderAutoDeductedBadge = () => {
      if (!schedule.auto_deducted) {
        return null;
      }

      return (
        <span className="bg-blue-bell-100 text-blue-bell-900 dark:bg-blue-bell-900 dark:text-blue-bell-100 rounded-full px-2 py-1 text-xs font-bold">
          Auto-deducted
        </span>
      );
    };

    const renderImportantBadge = () => {
      if (!isImportant) {
        return null;
      }

      return (
        <span className="bg-sweet-corn-100 text-sweet-corn-900 dark:bg-sweet-corn-900 dark:text-sweet-corn-100 rounded-full px-2 py-1 text-xs font-bold">
          Important
        </span>
      );
    };

    return (
      <span className="flex flex-wrap justify-end gap-2 sm:col-start-2">
        {renderAutoDeductedBadge()}
        {renderImportantBadge()}
      </span>
    );
  };

  const renderWeekendBadge = (schedule: PaymentScheduleFormState) => {
    if (
      schedule.timing !== ExpensePaymentTiming.DAY_OF_MONTH ||
      schedule.day_of_month === '' ||
      income.next_pay_date === ''
    ) {
      return null;
    }

    const representativeDate = new Date(`${income.next_pay_date}T12:00:00`);
    representativeDate.setDate(Number.parseInt(schedule.day_of_month, 10));

    if (
      representativeDate.getDay() !== 0 &&
      representativeDate.getDay() !== 6
    ) {
      return null;
    }

    return (
      <span className="text-storm-dust-500 dark:text-storm-dust-400 text-xs sm:col-start-2 sm:text-right">
        Weekend occurrence moves to Monday
      </span>
    );
  };

  const getUtilityLabel = () => {
    if (expenses.utility_type === UtilityType.CUSTOM) {
      return expenses.utility_custom_label;
    }

    if (expenses.utility_type === UtilityType.WATER_AND_ELECTRICITY) {
      return 'Water + electricity';
    }

    if (expenses.utility_type === UtilityType.ELECTRICITY) {
      return 'Electricity';
    }

    if (expenses.utility_type === UtilityType.WATER) {
      return 'Water';
    }

    return 'Utilities';
  };

  const renderSchedule = (
    sourceKey: string,
    label: string,
    amount: string,
    schedule: PaymentScheduleFormState
  ) => {
    if (!hasPositiveAmount(amount)) {
      return null;
    }

    return (
      <li
        key={sourceKey}
        className="border-storm-dust-200 dark:border-storm-dust-700 grid gap-2 border-b py-4 last:border-b-0 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"
      >
        <span className="min-w-0">
          <strong className="text-storm-dust-900 dark:text-storm-dust-50 block truncate">
            {label}
          </strong>
          <span>{formatCentsAsCurrency(dollarsToCents(amount))}</span>
        </span>
        <span className="font-semibold sm:text-right">
          {getScheduleDescription(schedule)}
        </span>
        {renderScheduleBadges(sourceKey, schedule)}
        {renderWeekendBadge(schedule)}
      </li>
    );
  };

  const renderMiscSchedules = () => {
    return expenses.misc_expenses.map((expense, index) =>
      renderSchedule(
        `misc:${index}`,
        expense.label,
        expense.amount_dollars,
        expense.payment_schedule
      )
    );
  };

  const renderDebtSchedules = () => {
    return debts.debts.map((debt, index) =>
      renderSchedule(
        `debt:${index}`,
        debt.label,
        debt.current_payment_dollars,
        debt.payment_schedule
      )
    );
  };

  const renderInternetSchedule = () => {
    if (expenses.utilities_includes_internet) {
      return null;
    }

    return renderSchedule(
      'internet',
      'Internet',
      expenses.internet_dollars,
      expenses.payment_schedules.internet
    );
  };

  const renderIncludedServices = () => {
    const includedServices: string[] = [];

    if (expenses.utilities_includes_internet) {
      includedServices.push('Internet');
    }

    if (expenses.utilities_includes_cable) {
      includedServices.push('Cable');
    }

    if (includedServices.length === 0) {
      return null;
    }

    return (
      <li className="text-storm-dust-500 dark:text-storm-dust-400 pb-3 text-sm">
        Utilities includes {includedServices.join(' and ')}
      </li>
    );
  };

  return (
    <div className="flex flex-col gap-6 py-4">
      <div className="flex flex-col items-center gap-4 text-center">
        <div aria-hidden="true" className="text-5xl">
          &#127881;
        </div>
        <h3 className="text-storm-dust-900 dark:text-storm-dust-50 text-2xl font-bold">
          You&apos;re all set!
        </h3>
        <p className="text-storm-dust-600 dark:text-storm-dust-300 max-w-sm text-sm">
          Your profile is complete. Click <strong>Finish</strong> to start using
          Finance Harbour and take control of your finances.
        </p>
      </div>
      <section aria-labelledby="payment-schedule-review-title">
        <h4
          id="payment-schedule-review-title"
          className="text-storm-dust-900 dark:text-storm-dust-50 mb-2 font-semibold"
        >
          Payment schedule
        </h4>
        <ul className="text-storm-dust-700 dark:text-storm-dust-200 text-sm">
          {renderSchedule(
            'rent_or_mortgage',
            'Rent or mortgage',
            expenses.rent_or_mortgage_dollars,
            expenses.payment_schedules.rent_or_mortgage
          )}
          {renderSchedule(
            'utilities',
            getUtilityLabel(),
            expenses.utilities_dollars,
            expenses.payment_schedules.utilities
          )}
          {renderIncludedServices()}
          {renderSchedule(
            'food',
            'Food',
            expenses.food_dollars,
            expenses.payment_schedules.food
          )}
          {renderInternetSchedule()}
          {renderSchedule(
            'phone',
            'Phone',
            expenses.phone_dollars,
            expenses.payment_schedules.phone
          )}
          {renderSchedule(
            'car_payment',
            'Car payment',
            expenses.car_payment_dollars,
            expenses.payment_schedules.car_payment
          )}
          {renderSchedule(
            'insurance',
            'Insurance',
            expenses.insurance_dollars,
            expenses.payment_schedules.insurance
          )}
          {renderMiscSchedules()}
          {renderDebtSchedules()}
        </ul>
      </section>
    </div>
  );
};

export default ConcludeStep;
