import {
  DebtBalanceReviewStatus,
  PayChequeReviewStatus,
  PaymentReviewStatus,
} from 'components/pages/payday/enums/payday-status';
import PaydayDebtBalanceFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-debt-balance-field-errors-definition';
import PaydayLineItemFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-line-item-field-errors-definition';
import PaydayPayChequeFieldErrorsDefinition from 'components/pages/payday/validations/hooks/definitions/payday-pay-cheque-field-errors-definition';
import UsePaydayFormValidationDefinition from 'components/pages/payday/validations/hooks/definitions/use-payday-form-validation-definition';

export const usePaydayFormValidation =
  (): UsePaydayFormValidationDefinition => {
    const validatePayChequeStep: UsePaydayFormValidationDefinition['validatePayChequeStep'] =
      (request) => {
        const fieldErrors: PaydayPayChequeFieldErrorsDefinition = {};
        const requiresAmount =
          request.review_status === PayChequeReviewStatus.CONFIRMED;
        const amountIsInvalid =
          request.actual_amount_cents === null ||
          !Number.isInteger(request.actual_amount_cents) ||
          request.actual_amount_cents < 0 ||
          request.actual_amount_cents > 2147483647;
        if (request.review_status === PayChequeReviewStatus.UNREVIEWED) {
          return {
            is_valid: false,
            step_error: 'Confirm the pay cheque or choose I do not remember.',
            field_errors: fieldErrors,
          };
        }

        if (requiresAmount && amountIsInvalid) {
          return {
            is_valid: false,
            step_error: 'Enter a valid actual pay cheque amount.',
            field_errors: {
              actual_amount_cents: 'Enter a non-negative dollar amount.',
            },
          };
        }

        return { is_valid: true, step_error: null, field_errors: fieldErrors };
      };

    const validateLineItemStep: UsePaydayFormValidationDefinition['validateLineItemStep'] =
      (request) => {
        const fieldErrors: PaydayLineItemFieldErrorsDefinition = {};
        const requiresAmount =
          request.review_status === PaymentReviewStatus.PAID;
        const amountIsInvalid =
          request.actual_amount_cents === null ||
          !Number.isInteger(request.actual_amount_cents) ||
          request.actual_amount_cents < 0 ||
          request.actual_amount_cents > 2147483647;
        const requiresScheduledAmount =
          request.review_status === PaymentReviewStatus.SCHEDULED;
        const scheduledAmountIsInvalid =
          request.scheduled_amount_cents === null ||
          !Number.isInteger(request.scheduled_amount_cents) ||
          request.scheduled_amount_cents < 0 ||
          request.scheduled_amount_cents > 2147483647;

        if (requiresAmount && amountIsInvalid) {
          return {
            is_valid: false,
            step_error: 'Enter a valid actual payment amount.',
            field_errors: {
              actual_amount_cents: 'Enter a non-negative dollar amount.',
            },
          };
        }

        if (request.review_status === PaymentReviewStatus.UNREVIEWED) {
          return {
            is_valid: false,
            step_error: 'Choose Paid, Not paid, or I do not remember.',
            field_errors: fieldErrors,
          };
        }

        if (requiresScheduledAmount && scheduledAmountIsInvalid) {
          return {
            is_valid: false,
            step_error: 'Enter a valid expected payment amount.',
            field_errors: {
              scheduled_amount_cents: 'Enter a non-negative dollar amount.',
            },
          };
        }

        return { is_valid: true, step_error: null, field_errors: fieldErrors };
      };

    const validateDebtBalanceStep: UsePaydayFormValidationDefinition['validateDebtBalanceStep'] =
      (request) => {
        const fieldErrors: PaydayDebtBalanceFieldErrorsDefinition = {};
        const requiresAmount =
          request.review_status === DebtBalanceReviewStatus.CONFIRMED;
        const amountIsInvalid =
          request.actual_balance_cents === null ||
          !Number.isInteger(request.actual_balance_cents) ||
          request.actual_balance_cents < 0 ||
          request.actual_balance_cents > 2147483647;

        if (requiresAmount && amountIsInvalid) {
          return {
            is_valid: false,
            step_error: 'Enter a valid actual debt balance.',
            field_errors: {
              actual_balance_cents: 'Enter a non-negative dollar amount.',
            },
          };
        }

        if (request.review_status === DebtBalanceReviewStatus.UNREVIEWED) {
          return {
            is_valid: false,
            step_error: 'Confirm the balance or choose I do not remember.',
            field_errors: fieldErrors,
          };
        }

        return { is_valid: true, step_error: null, field_errors: fieldErrors };
      };

    return {
      validatePayChequeStep,
      validateLineItemStep,
      validateDebtBalanceStep,
    };
  };
