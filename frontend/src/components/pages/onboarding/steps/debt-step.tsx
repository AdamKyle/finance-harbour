import React, { ChangeEvent } from 'react';

import { DebtEntryStringFieldName } from 'components/pages/onboarding/types/debt-entry-form-state';
import DebtStepProps from 'components/pages/onboarding/types/debt-step-props';
import { DebtFieldErrorsDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/payment-schedule/enums/paycheck-position';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import Input from 'ui/form-elements/input';

const DebtStep = ({
  request,
  setRequest,
  stepError,
  fieldErrors = [],
}: DebtStepProps) => {
  const handleAddDebt = () => {
    setRequest({
      debts: [
        ...request.debts,
        {
          label: '',
          current_balance_dollars: '',
          minimum_payment_dollars: '',
          current_payment_dollars: '',
          payment_schedule: {
            timing: ExpensePaymentTiming.PAYCHECK_POSITION,
            paycheck_position: PaycheckPosition.FIRST,
            day_of_month: '',
            auto_deducted: false,
          },
        },
      ],
    });
  };

  const handleRemoveDebt = (index: number) => {
    setRequest({
      debts: request.debts.filter((_, debtIndex) => debtIndex !== index),
    });
  };

  const handleDebtChange = (
    index: number,
    field: DebtEntryStringFieldName,
    value: string
  ) => {
    const updatedDebts = request.debts.map((debt, debtIndex) => {
      if (debtIndex !== index) {
        return debt;
      }

      return { ...debt, [field]: value };
    });

    setRequest({ debts: updatedDebts });
  };

  const renderStepError = () => {
    if (!stepError) {
      return null;
    }

    return <Alert variant={AlertVariant.DANGER}>{stepError}</Alert>;
  };

  return (
    <div className="flex flex-col gap-6">
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Add each debt you carry. Enter amounts in dollars. At least one debt is
        required.
      </p>

      {renderStepError()}

      {request.debts.map((debt, index) => {
        let debtErrors: DebtFieldErrorsDefinition = {};
        let debtTitle = `Debt ${index + 1}`;

        if (fieldErrors[index] !== undefined) {
          debtErrors = fieldErrors[index];
        }

        if (debt.label.trim() !== '') {
          debtTitle = debt.label.trim();
        }

        return (
          <div
            key={index}
            className="flex flex-col gap-4 rounded-lg border border-gray-200 p-4 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <span className="text-storm-dust-800 dark:text-storm-dust-100 font-semibold">
                {debtTitle}
              </span>
              <Button
                label="Remove"
                variant={ButtonVariant.DANGER}
                on_click={() => {
                  handleRemoveDebt(index);
                }}
              />
            </div>

            <Input
              id={`debt-label-${index}`}
              label="Label (e.g. VISA, Student Loan)"
              name={`debt-label-${index}`}
              type="text"
              value={debt.label}
              error={debtErrors.label}
              has_error={debtErrors.label !== undefined}
              onChange={(e: ChangeEvent<HTMLInputElement>) => {
                handleDebtChange(index, 'label', e.target.value);
              }}
            />
            <Input
              id={`debt-balance-${index}`}
              label="Current balance ($)"
              name={`debt-balance-${index}`}
              type="text"
              placeholder="0.00"
              value={debt.current_balance_dollars}
              error={debtErrors.current_balance_dollars}
              has_error={debtErrors.current_balance_dollars !== undefined}
              onChange={(e: ChangeEvent<HTMLInputElement>) => {
                handleDebtChange(
                  index,
                  'current_balance_dollars',
                  e.target.value
                );
              }}
            />
            <Input
              id={`debt-min-payment-${index}`}
              label="Minimum payment ($)"
              name={`debt-min-payment-${index}`}
              type="text"
              placeholder="0.00"
              value={debt.minimum_payment_dollars}
              error={debtErrors.minimum_payment_dollars}
              has_error={debtErrors.minimum_payment_dollars !== undefined}
              required
              onChange={(e: ChangeEvent<HTMLInputElement>) => {
                handleDebtChange(
                  index,
                  'minimum_payment_dollars',
                  e.target.value
                );
              }}
            />
            <Input
              id={`debt-current-payment-${index}`}
              label="Current payment ($)"
              name={`debt-current-payment-${index}`}
              type="text"
              placeholder="0.00"
              value={debt.current_payment_dollars}
              error={debtErrors.current_payment_dollars}
              has_error={debtErrors.current_payment_dollars !== undefined}
              required
              onChange={(e: ChangeEvent<HTMLInputElement>) => {
                handleDebtChange(
                  index,
                  'current_payment_dollars',
                  e.target.value
                );
              }}
            />
          </div>
        );
      })}

      <Button
        label="+ Add debt"
        variant={ButtonVariant.PRIMARY}
        on_click={handleAddDebt}
      />
    </div>
  );
};

export default DebtStep;
