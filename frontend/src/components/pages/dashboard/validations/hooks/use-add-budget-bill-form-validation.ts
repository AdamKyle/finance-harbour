import { validateDollarInput } from 'lib/money/money';

import AddBudgetBillFieldErrorsDefinition from 'components/pages/dashboard/validations/hooks/definitions/add-budget-bill-field-errors-definition';
import UseAddBudgetBillFormValidationDefinition from 'components/pages/dashboard/validations/hooks/definitions/use-add-budget-bill-form-validation-definition';

export const useAddBudgetBillFormValidation =
  (): UseAddBudgetBillFormValidationDefinition => {
    const validateAddBudgetBill: UseAddBudgetBillFormValidationDefinition['validateAddBudgetBill'] =
      (requestData) => {
        const fieldErrors: AddBudgetBillFieldErrorsDefinition = {};

        if (requestData.title.trim() === '') {
          fieldErrors.title = 'Enter a bill name.';
        }

        if (requestData.amount_dollars === '') {
          fieldErrors.amount_dollars = 'Enter a bill amount.';
        } else {
          const amountValidation = validateDollarInput(
            requestData.amount_dollars
          );

          if (!amountValidation.valid) {
            fieldErrors.amount_dollars = amountValidation.error;
          }
        }

        const isValid = Object.keys(fieldErrors).length === 0;

        if (isValid) {
          return {
            is_valid: true,
            step_error: '',
            field_errors: fieldErrors,
          };
        }

        return {
          is_valid: false,
          step_error: 'Fix the errors below before adding this bill.',
          field_errors: fieldErrors,
        };
      };

    return { validateAddBudgetBill };
  };
