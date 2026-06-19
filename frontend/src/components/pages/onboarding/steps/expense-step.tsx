import React, { ChangeEvent } from 'react';

import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import ExpenseStepProps from 'components/pages/onboarding/types/expense-step-props';
import { MiscExpenseEntryFormState } from 'components/pages/onboarding/types/misc-expense-entry-form-state';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import Input from 'ui/form-elements/input';

const ExpenseStep = ({
  request,
  setRequest,
  stepError,
  fieldErrors = {},
}: ExpenseStepProps) => {
  const handleFieldChange = (
    key: keyof Omit<ExpenseStepFormState, 'misc_expenses'>,
    value: string
  ) => {
    setRequest({ ...request, [key]: value });
  };

  const handleAddMisc = () => {
    setRequest({
      ...request,
      misc_expenses: [
        ...request.misc_expenses,
        {
          label: '',
          amount_dollars: '',
        },
      ],
    });
  };

  const handleRemoveMisc = (index: number) => {
    setRequest({
      ...request,
      misc_expenses: request.misc_expenses.filter(
        (_, miscExpenseIndex) => miscExpenseIndex !== index
      ),
    });
  };

  const handleMiscChange = (
    index: number,
    field: keyof MiscExpenseEntryFormState,
    value: string
  ) => {
    const updatedMiscExpenses = request.misc_expenses.map(
      (entry, miscExpenseIndex) =>
        miscExpenseIndex === index ? { ...entry, [field]: value } : entry
    );

    setRequest({ ...request, misc_expenses: updatedMiscExpenses });
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
        Enter your monthly expenses in dollars. At least one expense is
        required. Leave fields blank if they do not apply.
      </p>

      {renderStepError()}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          id="expense-rent-or-mortgage"
          label="Rent or mortgage ($)"
          name="rent_or_mortgage_dollars"
          type="text"
          placeholder="0.00"
          value={request.rent_or_mortgage_dollars}
          error={fieldErrors.rent_or_mortgage_dollars}
          has_error={fieldErrors.rent_or_mortgage_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('rent_or_mortgage_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-water"
          label="Water ($)"
          name="water_dollars"
          type="text"
          placeholder="0.00"
          value={request.water_dollars}
          error={fieldErrors.water_dollars}
          has_error={fieldErrors.water_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('water_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-electricity"
          label="Electricity ($)"
          name="electricity_dollars"
          type="text"
          placeholder="0.00"
          value={request.electricity_dollars}
          error={fieldErrors.electricity_dollars}
          has_error={fieldErrors.electricity_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('electricity_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-food"
          label="Food ($)"
          name="food_dollars"
          type="text"
          placeholder="0.00"
          value={request.food_dollars}
          error={fieldErrors.food_dollars}
          has_error={fieldErrors.food_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('food_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-internet"
          label="Internet ($)"
          name="internet_dollars"
          type="text"
          placeholder="0.00"
          value={request.internet_dollars}
          error={fieldErrors.internet_dollars}
          has_error={fieldErrors.internet_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('internet_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-phone"
          label="Phone ($)"
          name="phone_dollars"
          type="text"
          placeholder="0.00"
          value={request.phone_dollars}
          error={fieldErrors.phone_dollars}
          has_error={fieldErrors.phone_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('phone_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-car-payment"
          label="Car payment ($)"
          name="car_payment_dollars"
          type="text"
          placeholder="0.00"
          value={request.car_payment_dollars}
          error={fieldErrors.car_payment_dollars}
          has_error={fieldErrors.car_payment_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('car_payment_dollars', event.target.value);
          }}
        />
        <Input
          id="expense-insurance"
          label="Insurance ($)"
          name="insurance_dollars"
          type="text"
          placeholder="0.00"
          value={request.insurance_dollars}
          error={fieldErrors.insurance_dollars}
          has_error={fieldErrors.insurance_dollars !== undefined}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            handleFieldChange('insurance_dollars', event.target.value);
          }}
        />
      </div>

      <div className="flex flex-col gap-4">
        <span className="text-storm-dust-800 dark:text-storm-dust-100 text-sm font-semibold">
          Other expenses
        </span>

        {request.misc_expenses.map((entry, index) => {
          const miscExpenseErrors = fieldErrors.misc_expenses?.[index] ?? {};

          return (
            <div
              key={index}
              className="flex flex-col gap-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700"
            >
              <div className="flex items-center justify-between">
                <span className="text-storm-dust-700 dark:text-storm-dust-200 text-sm font-medium">
                  Other expense {index + 1}
                </span>
                <Button
                  label="Remove"
                  variant={ButtonVariant.DANGER}
                  on_click={() => {
                    handleRemoveMisc(index);
                  }}
                />
              </div>
              <Input
                id={`misc-label-${index}`}
                label="Label"
                name={`misc-label-${index}`}
                type="text"
                placeholder="e.g. Gym membership"
                value={entry.label}
                error={miscExpenseErrors.label}
                has_error={miscExpenseErrors.label !== undefined}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  handleMiscChange(index, 'label', e.target.value);
                }}
              />
              <Input
                id={`misc-amount-${index}`}
                label="Amount ($)"
                name={`misc-amount-${index}`}
                type="text"
                placeholder="0.00"
                value={entry.amount_dollars}
                error={miscExpenseErrors.amount_dollars}
                has_error={miscExpenseErrors.amount_dollars !== undefined}
                onChange={(e: ChangeEvent<HTMLInputElement>) => {
                  handleMiscChange(index, 'amount_dollars', e.target.value);
                }}
              />
            </div>
          );
        })}

        <Button
          label="+ Add other expense"
          variant={ButtonVariant.PRIMARY}
          on_click={handleAddMisc}
        />
      </div>
    </div>
  );
};

export default ExpenseStep;
