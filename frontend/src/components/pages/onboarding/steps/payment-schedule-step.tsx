import React from 'react';

import { dollarsToCents, formatCentsAsCurrency } from 'lib/money/money';

import { UtilityType } from 'components/pages/onboarding/enums/utility-type';
import PaymentScheduleStepProps from 'components/pages/onboarding/types/payment-schedule-step-props';
import PaymentScheduleFields from 'components/payment-schedule/payment-schedule-fields';
import { CommonExpenseSourceKey } from 'components/payment-schedule/types/payment-schedule-form-state';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';

const PaymentScheduleStep = ({
  debts,
  expenses,
  income,
  setDebts,
  setExpenses,
  stepError,
  fieldErrors = {},
}: PaymentScheduleStepProps) => {
  const representativeDate = income.next_pay_date;

  const hasPositiveAmount = (amount: string) => {
    if (amount.trim() === '') {
      return false;
    }

    return dollarsToCents(amount) > 0;
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

  const handleCommonScheduleChange = (
    sourceKey: CommonExpenseSourceKey,
    schedule: (typeof expenses.payment_schedules)[CommonExpenseSourceKey]
  ) => {
    setExpenses({
      ...expenses,
      payment_schedules: {
        ...expenses.payment_schedules,
        [sourceKey]: schedule,
      },
    });
  };

  const renderStepError = () => {
    if (!stepError) {
      return null;
    }

    return <Alert variant={AlertVariant.DANGER}>{stepError}</Alert>;
  };

  const renderScheduleRow = (
    sourceKey: CommonExpenseSourceKey,
    label: string,
    amount: string
  ) => {
    if (!hasPositiveAmount(amount)) {
      return null;
    }

    return (
      <li
        key={sourceKey}
        className="border-storm-dust-200 dark:border-storm-dust-700 border-b py-5 last:border-b-0"
      >
        <p className="text-storm-dust-900 dark:text-storm-dust-50 mb-3 font-semibold">
          {label} — {formatCentsAsCurrency(dollarsToCents(amount))}
        </p>
        <PaymentScheduleFields
          id={`schedule-${sourceKey}`}
          label={label.toLowerCase()}
          representative_date={representativeDate}
          pay_period_type={income.pay_period_type}
          show_large_bill_hint={sourceKey === 'rent_or_mortgage'}
          schedule={expenses.payment_schedules[sourceKey]}
          error={fieldErrors[sourceKey]}
          on_change={(schedule) => {
            handleCommonScheduleChange(sourceKey, schedule);
          }}
        />
      </li>
    );
  };

  const renderDebtRows = () => {
    return debts.debts.map((debt, index) => {
      if (!hasPositiveAmount(debt.current_payment_dollars)) {
        return null;
      }

      const sourceKey = `debt:${index}`;

      return (
        <li
          key={sourceKey}
          className="border-storm-dust-200 dark:border-storm-dust-700 border-b py-5 last:border-b-0"
        >
          <p className="text-storm-dust-900 dark:text-storm-dust-50 mb-3 font-semibold">
            {debt.label} —{' '}
            {formatCentsAsCurrency(
              dollarsToCents(debt.current_payment_dollars)
            )}
          </p>
          <PaymentScheduleFields
            id={`schedule-${sourceKey}`}
            label={debt.label}
            representative_date={representativeDate}
            pay_period_type={income.pay_period_type}
            schedule={debt.payment_schedule}
            error={fieldErrors[sourceKey]}
            on_change={(paymentSchedule) => {
              const updatedDebts = debts.debts.map((entry, debtIndex) => {
                if (debtIndex !== index) {
                  return entry;
                }

                return { ...entry, payment_schedule: paymentSchedule };
              });

              setDebts({ debts: updatedDebts });
            }}
          />
        </li>
      );
    });
  };

  const renderInternetSchedule = () => {
    if (expenses.utilities_includes_internet) {
      return null;
    }

    return renderScheduleRow('internet', 'Internet', expenses.internet_dollars);
  };

  const renderMiscExpenseRows = () => {
    return expenses.misc_expenses.map((expense, index) => {
      if (!hasPositiveAmount(expense.amount_dollars)) {
        return null;
      }

      const sourceKey = `misc:${index}`;

      return (
        <li
          key={sourceKey}
          className="border-storm-dust-200 dark:border-storm-dust-700 border-b py-5 last:border-b-0"
        >
          <p className="text-storm-dust-900 dark:text-storm-dust-50 mb-3 font-semibold">
            {expense.label} —{' '}
            {formatCentsAsCurrency(dollarsToCents(expense.amount_dollars))}
          </p>
          <PaymentScheduleFields
            id={`schedule-${sourceKey}`}
            label={expense.label}
            representative_date={representativeDate}
            pay_period_type={income.pay_period_type}
            schedule={expense.payment_schedule}
            error={fieldErrors[sourceKey]}
            on_change={(paymentSchedule) => {
              const updatedExpenses = expenses.misc_expenses.map(
                (entry, expenseIndex) => {
                  if (expenseIndex !== index) {
                    return entry;
                  }

                  return { ...entry, payment_schedule: paymentSchedule };
                }
              );

              setExpenses({ ...expenses, misc_expenses: updatedExpenses });
            }}
          />
        </li>
      );
    });
  };

  return (
    <div className="flex flex-col gap-4">
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Your pay schedule starts {income.next_pay_date}. Choose whether each
        payment belongs on every paycheck, a particular paycheck in the month,
        or a recurring monthly date.
      </p>
      {renderStepError()}
      <ul>
        {renderScheduleRow(
          'rent_or_mortgage',
          'Rent or mortgage',
          expenses.rent_or_mortgage_dollars
        )}
        {renderScheduleRow(
          'utilities',
          getUtilityLabel(),
          expenses.utilities_dollars
        )}
        {renderScheduleRow('food', 'Food', expenses.food_dollars)}
        {renderInternetSchedule()}
        {renderScheduleRow('phone', 'Phone', expenses.phone_dollars)}
        {renderScheduleRow(
          'car_payment',
          'Car payment',
          expenses.car_payment_dollars
        )}
        {renderScheduleRow(
          'insurance',
          'Insurance',
          expenses.insurance_dollars
        )}
        {renderMiscExpenseRows()}
        {renderDebtRows()}
      </ul>
    </div>
  );
};

export default PaymentScheduleStep;
