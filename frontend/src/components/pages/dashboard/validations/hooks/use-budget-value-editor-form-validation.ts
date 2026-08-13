import { dollarsToCents, validateDollarInput } from 'lib/money/money';
import { parseDecimalInput } from 'lib/numeric/parse-decimal-input';

import { BudgetValueField } from 'components/pages/dashboard/api/enums/budget-value-field';
import BudgetValueEditorFieldErrorsDefinition from 'components/pages/dashboard/validations/hooks/definitions/budget-value-editor-field-errors-definition';
import UseBudgetValueEditorFormValidationDefinition from 'components/pages/dashboard/validations/hooks/definitions/use-budget-value-editor-form-validation-definition';

export const useBudgetValueEditorFormValidation =
  (): UseBudgetValueEditorFormValidationDefinition => {
    const getSupportedRangeError = (amountDollars: string) => {
      const amountCents = dollarsToCents(amountDollars);

      if (amountCents < -2147483648 || amountCents > 2147483647) {
        return 'This amount is outside the supported range.';
      }

      return undefined;
    };

    const validateBudgetValueEditor: UseBudgetValueEditorFormValidationDefinition['validateBudgetValueEditor'] =
      (field, amountDollars) => {
        const fieldErrors: BudgetValueEditorFieldErrorsDefinition = {};

        if (amountDollars === '') {
          fieldErrors.amount_dollars = 'Enter an amount.';
        } else if (
          field === BudgetValueField.PAY_CHEQUE ||
          field === BudgetValueField.LINE_ITEM
        ) {
          const validationResult = validateDollarInput(amountDollars);

          if (!validationResult.valid) {
            fieldErrors.amount_dollars = validationResult.error;
          }
        } else {
          const parseResult = parseDecimalInput(amountDollars, false);

          if (!parseResult.is_valid) {
            fieldErrors.amount_dollars =
              'Enter a valid dollar amount (e.g. -123.45).';
          }
        }

        if (fieldErrors.amount_dollars === undefined) {
          fieldErrors.amount_dollars = getSupportedRangeError(amountDollars);
        }

        const isValid = fieldErrors.amount_dollars === undefined;

        if (isValid) {
          return {
            is_valid: true,
            step_error: '',
            field_errors: fieldErrors,
          };
        }

        return {
          is_valid: false,
          step_error: 'Fix this amount before saving.',
          field_errors: fieldErrors,
        };
      };

    return { validateBudgetValueEditor };
  };
