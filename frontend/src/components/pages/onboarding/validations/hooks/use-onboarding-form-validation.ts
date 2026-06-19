import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import {
  dollarsToCents,
  validateDollarInput,
  validateInterestRateInput,
  validatePositiveDollarInput,
} from 'components/pages/onboarding/utils/money';
import {
  DebtFieldErrorsDefinition,
  ExpenseFieldErrorsDefinition,
  IncomeFieldErrorsDefinition,
  LeftOverWarningFieldErrorsDefinition,
  MiscExpenseFieldErrorsDefinition,
  ProfileFieldErrorsDefinition,
} from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { UseOnboardingFormValidationDefinition } from 'components/pages/onboarding/validations/hooks/definitions/use-onboarding-form-validation-definition';

export const useOnboardingFormValidation =
  (): UseOnboardingFormValidationDefinition => {
    const validateProfileStep: UseOnboardingFormValidationDefinition['validateProfileStep'] =
      (profileForm) => {
        const fieldErrors: ProfileFieldErrorsDefinition = {};

        if (profileForm.nickname.trim() === '') {
          fieldErrors.nickname = 'Enter a nickname.';
        }

        if (profileForm.nickname.length > 100) {
          fieldErrors.nickname = 'Nickname must be 100 characters or fewer.';
        }

        return {
          is_valid: Object.keys(fieldErrors).length === 0,
          step_error: '',
          field_errors: fieldErrors,
        };
      };

    const validateDebtStep: UseOnboardingFormValidationDefinition['validateDebtStep'] =
      (debtForm) => {
        if (debtForm.debts.length === 0) {
          return {
            is_valid: false,
            step_error: 'Add at least one debt to continue.',
            field_errors: [],
          };
        }

        const fieldErrors = debtForm.debts.map((debtEntry) => {
          const debtFieldErrors: DebtFieldErrorsDefinition = {};

          if (!debtEntry.label.trim()) {
            debtFieldErrors.label = 'Label is required';
          }

          const balanceValidation = validatePositiveDollarInput(
            debtEntry.current_balance_dollars,
            'Current balance'
          );

          if (!balanceValidation.valid) {
            debtFieldErrors.current_balance_dollars = balanceValidation.error;
          }

          const interestValidation = validateInterestRateInput(
            debtEntry.interest_rate_percent
          );

          if (!interestValidation.valid) {
            debtFieldErrors.interest_rate_percent = interestValidation.error;
          }

          const minimumPaymentValidation = validatePositiveDollarInput(
            debtEntry.minimum_payment_dollars,
            'Minimum payment'
          );

          if (!minimumPaymentValidation.valid) {
            debtFieldErrors.minimum_payment_dollars =
              minimumPaymentValidation.error;
          }

          const currentPaymentValidation = validatePositiveDollarInput(
            debtEntry.current_payment_dollars,
            'Current payment'
          );

          if (!currentPaymentValidation.valid) {
            debtFieldErrors.current_payment_dollars =
              currentPaymentValidation.error;
          }

          return debtFieldErrors;
        });

        const hasFieldErrors = fieldErrors.some(
          (debtFieldErrors) => Object.keys(debtFieldErrors).length > 0
        );

        if (!hasFieldErrors) {
          return {
            is_valid: true,
            step_error: '',
            field_errors: fieldErrors,
          };
        }

        return {
          is_valid: false,
          step_error: 'Fix the errors below before continuing.',
          field_errors: fieldErrors,
        };
      };

    const validateIncomeStep: UseOnboardingFormValidationDefinition['validateIncomeStep'] =
      (incomeForm) => {
        const fieldErrors: IncomeFieldErrorsDefinition = {};

        const incomeValidation = validatePositiveDollarInput(
          incomeForm.income_per_pay_period_dollars,
          'Income'
        );

        if (!incomeValidation.valid) {
          fieldErrors.income_per_pay_period_dollars = incomeValidation.error;
        }

        if (!incomeForm.pay_period_type) {
          fieldErrors.pay_period_type = 'Select a pay period';
        }

        return {
          is_valid: Object.keys(fieldErrors).length === 0,
          step_error: '',
          field_errors: fieldErrors,
        };
      };

    const validateExpenseStep: UseOnboardingFormValidationDefinition['validateExpenseStep'] =
      (expenseForm) => {
        const expenseFieldKeys: (keyof Omit<
          ExpenseStepFormState,
          'misc_expenses'
        >)[] = [
          'rent_or_mortgage_dollars',
          'water_dollars',
          'electricity_dollars',
          'food_dollars',
          'internet_dollars',
          'phone_dollars',
          'car_payment_dollars',
          'insurance_dollars',
        ];
        const fieldErrors: ExpenseFieldErrorsDefinition = {};

        for (const fieldKey of expenseFieldKeys) {
          const submittedValue = expenseForm[fieldKey];

          if (submittedValue !== '') {
            const validationResult = validateDollarInput(submittedValue);

            if (!validationResult.valid) {
              fieldErrors[fieldKey] = validationResult.error;
            }
          }
        }

        const miscExpenseFieldErrors = expenseForm.misc_expenses.map(
          (miscExpense) => {
            const miscFieldErrors: MiscExpenseFieldErrorsDefinition = {};
            const hasLabel = miscExpense.label.trim() !== '';
            const hasAmount = miscExpense.amount_dollars.trim() !== '';

            if (!hasLabel && !hasAmount) {
              return miscFieldErrors;
            }

            if (hasLabel && !hasAmount) {
              miscFieldErrors.amount_dollars =
                'Enter an amount, or remove this expense.';
            } else if (!hasLabel && hasAmount) {
              miscFieldErrors.label = 'Enter a label, or remove this expense.';
            } else {
              const validationResult = validateDollarInput(
                miscExpense.amount_dollars
              );

              if (!validationResult.valid) {
                miscFieldErrors.amount_dollars = validationResult.error;
              }
            }

            return miscFieldErrors;
          }
        );

        if (
          miscExpenseFieldErrors.some(
            (miscFieldErrors) => Object.keys(miscFieldErrors).length > 0
          )
        ) {
          fieldErrors.misc_expenses = miscExpenseFieldErrors;
        }

        const hasPositiveCommonExpense = expenseFieldKeys.some(
          (fieldKey) =>
            validateDollarInput(expenseForm[fieldKey]).valid &&
            expenseForm[fieldKey] !== '' &&
            dollarsToCents(expenseForm[fieldKey]) > 0
        );
        const hasPositiveMiscExpense = expenseForm.misc_expenses.some(
          (miscExpense) =>
            miscExpense.label.trim() !== '' &&
            validateDollarInput(miscExpense.amount_dollars).valid &&
            miscExpense.amount_dollars !== '' &&
            dollarsToCents(miscExpense.amount_dollars) > 0
        );
        const hasFieldErrors = Object.keys(fieldErrors).length > 0;

        if (hasFieldErrors) {
          return {
            is_valid: false,
            step_error: 'Fix the errors below before continuing.',
            field_errors: fieldErrors,
          };
        }

        if (!hasPositiveCommonExpense && !hasPositiveMiscExpense) {
          return {
            is_valid: false,
            step_error: 'Enter at least one monthly expense greater than $0.',
            field_errors: {},
          };
        }

        return {
          is_valid: true,
          step_error: '',
          field_errors: {},
        };
      };

    const validateLeftOverWarningStep: UseOnboardingFormValidationDefinition['validateLeftOverWarningStep'] =
      (warningForm) => {
        const fieldErrors: LeftOverWarningFieldErrorsDefinition = {};
        const validationResult = validateDollarInput(
          warningForm.left_over_warning_amount_dollars
        );

        if (
          warningForm.left_over_warning_amount_dollars === '' ||
          !validationResult.valid
        ) {
          fieldErrors.left_over_warning_amount_dollars =
            validationResult.error ?? 'Enter a warning amount.';
        }

        return {
          is_valid: Object.keys(fieldErrors).length === 0,
          step_error: '',
          field_errors: fieldErrors,
        };
      };

    return {
      validateProfileStep,
      validateDebtStep,
      validateIncomeStep,
      validateExpenseStep,
      validateLeftOverWarningStep,
    };
  };
