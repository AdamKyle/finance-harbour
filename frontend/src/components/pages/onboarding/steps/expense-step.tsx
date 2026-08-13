import { ChangeEvent } from 'react';

import { ExpensePaymentTiming } from 'components/pages/onboarding/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/pages/onboarding/enums/paycheck-position';
import { UtilityType } from 'components/pages/onboarding/enums/utility-type';
import { ExpenseStringFieldName } from 'components/pages/onboarding/types/expense-step-form-state';
import ExpenseStepProps from 'components/pages/onboarding/types/expense-step-props';
import { MiscExpenseFieldErrorsDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import Input from 'ui/form-elements/input';
import MoneyInput from 'ui/form-elements/money-input';
import Select from 'ui/form-elements/select';

const ExpenseStep = ({
  request,
  setRequest,
  stepError,
  fieldErrors = {},
}: ExpenseStepProps) => {
  const handleStringChange = (
    fieldName: ExpenseStringFieldName,
    value: string
  ) => {
    setRequest({ ...request, [fieldName]: value });
  };

  const handleUtilityTypeChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const submittedType = event.target.value;
    let utilityType: UtilityType | '' = '';

    if (submittedType === UtilityType.ELECTRICITY) {
      utilityType = UtilityType.ELECTRICITY;
    } else if (submittedType === UtilityType.WATER) {
      utilityType = UtilityType.WATER;
    } else if (submittedType === UtilityType.WATER_AND_ELECTRICITY) {
      utilityType = UtilityType.WATER_AND_ELECTRICITY;
    } else if (submittedType === UtilityType.UTILITIES) {
      utilityType = UtilityType.UTILITIES;
    } else if (submittedType === UtilityType.CUSTOM) {
      utilityType = UtilityType.CUSTOM;
    }

    let includesInternet = false;
    let includesCable = false;

    if (utilityType === UtilityType.UTILITIES) {
      includesInternet = request.utilities_includes_internet;
      includesCable = request.utilities_includes_cable;
    }

    setRequest({
      ...request,
      utility_type: utilityType,
      utilities_includes_internet: includesInternet,
      utilities_includes_cable: includesCable,
    });
  };

  const handleIncludedServiceChange = (
    fieldName: 'utilities_includes_internet' | 'utilities_includes_cable',
    event: ChangeEvent<HTMLInputElement>
  ) => {
    setRequest({ ...request, [fieldName]: event.target.checked });
  };

  const handleAddMisc = () => {
    setRequest({
      ...request,
      misc_expenses: [
        ...request.misc_expenses,
        {
          label: '',
          amount_dollars: '',
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

  const handleRemoveMisc = (index: number) => {
    setRequest({
      ...request,
      misc_expenses: request.misc_expenses.filter(
        (_, expenseIndex) => expenseIndex !== index
      ),
    });
  };

  const renderStepError = () => {
    if (!stepError) {
      return null;
    }

    return <Alert variant={AlertVariant.DANGER}>{stepError}</Alert>;
  };

  const renderCustomUtilityLabel = () => {
    if (request.utility_type !== UtilityType.CUSTOM) {
      return null;
    }

    return (
      <Input
        id="utility-custom-label"
        label="Custom utility name"
        name="utility_custom_label"
        type="text"
        value={request.utility_custom_label}
        has_error={fieldErrors.utility_custom_label !== undefined}
        error={fieldErrors.utility_custom_label}
        placeholder="e.g. Municipal utilities"
        onChange={(event) => {
          handleStringChange('utility_custom_label', event.target.value);
        }}
      />
    );
  };

  const renderIncludedServices = () => {
    if (request.utility_type !== UtilityType.UTILITIES) {
      return null;
    }

    return (
      <fieldset className="border-storm-dust-200 dark:border-storm-dust-700 rounded-lg border p-4">
        <legend className="text-storm-dust-800 dark:text-storm-dust-100 px-1 text-sm font-semibold">
          Does this bill include other services?
        </legend>
        <div className="mt-2 flex flex-col gap-3 sm:flex-row sm:gap-6">
          <label className="flex min-h-11 items-center gap-3">
            <input
              type="checkbox"
              checked={request.utilities_includes_internet}
              onChange={(event) => {
                handleIncludedServiceChange(
                  'utilities_includes_internet',
                  event
                );
              }}
              className="accent-blue-bell-600 h-5 w-5"
            />
            <span>Internet</span>
          </label>
          <label className="flex min-h-11 items-center gap-3">
            <input
              type="checkbox"
              checked={request.utilities_includes_cable}
              onChange={(event) => {
                handleIncludedServiceChange('utilities_includes_cable', event);
              }}
              className="accent-blue-bell-600 h-5 w-5"
            />
            <span>Cable</span>
          </label>
        </div>
      </fieldset>
    );
  };

  const renderInternet = () => {
    if (request.utilities_includes_internet) {
      return null;
    }

    return (
      <MoneyInput
        id="expense-internet"
        label="Internet"
        name="internet_dollars"
        value={request.internet_dollars}
        has_error={fieldErrors.internet_dollars !== undefined}
        error={fieldErrors.internet_dollars}
        placeholder="0.00"
        on_value_change={(value) => {
          handleStringChange('internet_dollars', value);
        }}
      />
    );
  };

  const renderMiscExpenses = () => {
    return request.misc_expenses.map((entry, index) => {
      let errors: MiscExpenseFieldErrorsDefinition = {};

      if (fieldErrors.misc_expenses?.[index] !== undefined) {
        errors = fieldErrors.misc_expenses[index];
      }

      return (
        <div
          key={index}
          className="border-storm-dust-200 dark:border-storm-dust-700 flex flex-col gap-3 rounded-lg border p-4"
        >
          <div className="flex items-center justify-between">
            <span className="font-medium">Other expense {index + 1}</span>
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
            value={entry.label}
            has_error={errors.label !== undefined}
            error={errors.label}
            onChange={(event) => {
              const updatedExpenses = request.misc_expenses.map(
                (expense, expenseIndex) => {
                  if (expenseIndex !== index) {
                    return expense;
                  }

                  return { ...expense, label: event.target.value };
                }
              );

              setRequest({ ...request, misc_expenses: updatedExpenses });
            }}
          />
          <MoneyInput
            id={`misc-amount-${index}`}
            label="Amount"
            name={`misc-amount-${index}`}
            value={entry.amount_dollars}
            has_error={errors.amount_dollars !== undefined}
            error={errors.amount_dollars}
            on_value_change={(value) => {
              const updatedExpenses = request.misc_expenses.map(
                (expense, expenseIndex) => {
                  if (expenseIndex !== index) {
                    return expense;
                  }

                  return { ...expense, amount_dollars: value };
                }
              );

              setRequest({ ...request, misc_expenses: updatedExpenses });
            }}
          />
        </div>
      );
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        Enter each recurring monthly amount once. Combined utility services use
        one bill so they are never double counted.
      </p>
      {renderStepError()}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <MoneyInput
          id="expense-rent-or-mortgage"
          label="Rent or mortgage"
          name="rent_or_mortgage_dollars"
          value={request.rent_or_mortgage_dollars}
          has_error={fieldErrors.rent_or_mortgage_dollars !== undefined}
          error={fieldErrors.rent_or_mortgage_dollars}
          placeholder="0.00"
          on_value_change={(value) => {
            handleStringChange('rent_or_mortgage_dollars', value);
          }}
        />
        <Select
          id="utility-type"
          label="Utilities bill"
          name="utility_type"
          value={request.utility_type}
          has_error={fieldErrors.utility_type !== undefined}
          error={fieldErrors.utility_type}
          onChange={handleUtilityTypeChange}
        >
          <option value="">No utilities bill</option>
          <option value={UtilityType.ELECTRICITY}>Electricity</option>
          <option value={UtilityType.WATER}>Water</option>
          <option value={UtilityType.WATER_AND_ELECTRICITY}>
            Water + electricity
          </option>
          <option value={UtilityType.UTILITIES}>Utilities</option>
          <option value={UtilityType.CUSTOM}>Custom</option>
        </Select>
        {renderCustomUtilityLabel()}
        <MoneyInput
          id="expense-utilities"
          label="Utilities amount"
          name="utilities_dollars"
          value={request.utilities_dollars}
          has_error={fieldErrors.utilities_dollars !== undefined}
          error={fieldErrors.utilities_dollars}
          placeholder="0.00"
          on_value_change={(value) => {
            handleStringChange('utilities_dollars', value);
          }}
        />
      </div>
      {renderIncludedServices()}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <MoneyInput
          id="expense-food"
          label="Food"
          name="food_dollars"
          value={request.food_dollars}
          has_error={fieldErrors.food_dollars !== undefined}
          error={fieldErrors.food_dollars}
          placeholder="0.00"
          on_value_change={(value) => {
            handleStringChange('food_dollars', value);
          }}
        />
        {renderInternet()}
        <MoneyInput
          id="expense-phone"
          label="Phone"
          name="phone_dollars"
          value={request.phone_dollars}
          has_error={fieldErrors.phone_dollars !== undefined}
          error={fieldErrors.phone_dollars}
          placeholder="0.00"
          on_value_change={(value) => {
            handleStringChange('phone_dollars', value);
          }}
        />
        <MoneyInput
          id="expense-car-payment"
          label="Car payment"
          name="car_payment_dollars"
          value={request.car_payment_dollars}
          has_error={fieldErrors.car_payment_dollars !== undefined}
          error={fieldErrors.car_payment_dollars}
          placeholder="0.00"
          on_value_change={(value) => {
            handleStringChange('car_payment_dollars', value);
          }}
        />
        <MoneyInput
          id="expense-insurance"
          label="Insurance"
          name="insurance_dollars"
          value={request.insurance_dollars}
          has_error={fieldErrors.insurance_dollars !== undefined}
          error={fieldErrors.insurance_dollars}
          placeholder="0.00"
          on_value_change={(value) => {
            handleStringChange('insurance_dollars', value);
          }}
        />
      </div>
      <div className="flex flex-col gap-4">
        <h4 className="font-semibold">Other expenses</h4>
        {renderMiscExpenses()}
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
