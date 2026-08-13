import {
  validateDollarInput,
  validatePositiveDollarInput,
} from 'lib/money/money';

import { ExpensePaymentTiming } from 'components/payment-schedule/enums/expense-payment-timing';
import AddBillFormRequestDefinition from 'components/side-peeks/add-bill/api/hooks/definitions/add-bill-form-request-definition';
import { RecurringObligationKind } from 'components/side-peeks/add-bill/types/recurring-obligation-kind';
import AddBillFieldErrorsDefinition from 'components/side-peeks/add-bill/validations/hooks/definitions/add-bill-field-errors-definition';
import AddBillValidationResultDefinition from 'components/side-peeks/add-bill/validations/hooks/definitions/add-bill-validation-result-definition';
import UseAddBillFormValidationDefinition from 'components/side-peeks/add-bill/validations/hooks/definitions/use-add-bill-form-validation-definition';

export const useAddBillFormValidation =
  (): UseAddBillFormValidationDefinition => {
    const result = (
      fieldErrors: AddBillFieldErrorsDefinition
    ): AddBillValidationResultDefinition => {
      const isValid = Object.keys(fieldErrors).length === 0;

      return {
        is_valid: isValid,
        step_error: isValid ? '' : 'Fix the errors below before continuing.',
        field_errors: fieldErrors,
      };
    };

    const validateType = (request: AddBillFormRequestDefinition) => {
      const fieldErrors: AddBillFieldErrorsDefinition = {};

      if (request.kind === '') {
        fieldErrors.kind = 'Select Bill or Debt.';
      }

      return result(fieldErrors);
    };

    const validateDetails = (request: AddBillFormRequestDefinition) => {
      const fieldErrors: AddBillFieldErrorsDefinition = {};

      if (request.label.trim() === '') {
        fieldErrors.label = 'Enter a payment name.';
      }

      if (request.kind === RecurringObligationKind.BILL) {
        const amountResult = validatePositiveDollarInput(
          request.amount_dollars,
          'Recurring amount'
        );

        if (!amountResult.valid) {
          fieldErrors.amount_dollars = amountResult.error;
        }
      }

      if (request.kind === RecurringObligationKind.DEBT) {
        const balanceResult = validateDollarInput(
          request.current_balance_dollars
        );
        const minimumResult = validatePositiveDollarInput(
          request.minimum_payment_dollars,
          'Minimum payment'
        );
        const currentResult = validatePositiveDollarInput(
          request.current_payment_dollars,
          'Current payment'
        );

        if (request.current_balance_dollars === '' || !balanceResult.valid) {
          fieldErrors.current_balance_dollars =
            balanceResult.error ?? 'Enter a current balance.';
        }

        if (!minimumResult.valid) {
          fieldErrors.minimum_payment_dollars = minimumResult.error;
        }

        if (!currentResult.valid) {
          fieldErrors.current_payment_dollars = currentResult.error;
        }
      }

      return result(fieldErrors);
    };

    const validateSchedule = (request: AddBillFormRequestDefinition) => {
      const fieldErrors: AddBillFieldErrorsDefinition = {};
      const schedule = request.payment_schedule;

      if (schedule.timing === ExpensePaymentTiming.DAY_OF_MONTH) {
        const day = Number.parseInt(schedule.day_of_month, 10);

        if (!Number.isInteger(day) || day < 1 || day > 31) {
          fieldErrors.payment_schedule = 'Choose a recurring day from 1 to 31.';
        } else if (schedule.auto_deducted === null) {
          fieldErrors.payment_schedule =
            'Select whether this payment is automatically deducted.';
        }
      }

      return result(fieldErrors);
    };

    const validateStep = (
      step: number,
      request: AddBillFormRequestDefinition
    ) => {
      if (step === 0) {
        return validateType(request);
      }

      if (step === 1) {
        return validateDetails(request);
      }

      if (step === 2) {
        return validateSchedule(request);
      }

      return result({});
    };

    const validateAll = (request: AddBillFormRequestDefinition) => {
      const validations = [
        validateType(request),
        validateDetails(request),
        validateSchedule(request),
      ];
      const fieldErrors: AddBillFieldErrorsDefinition = {};

      validations.forEach((validation) =>
        Object.assign(fieldErrors, validation.field_errors)
      );

      return result(fieldErrors);
    };

    return { validateStep, validateAll };
  };
