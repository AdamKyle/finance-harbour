import UseBudgetPayDateValidationDefinition from './definitions/use-budget-pay-date-validation-definition';

export const useBudgetPayDateValidation =
  (): UseBudgetPayDateValidationDefinition => {
    const validatePayDate: UseBudgetPayDateValidationDefinition['validate_pay_date'] =
      (payDate, previousPayDate) => {
        const parsedDate = new Date(`${payDate}T12:00:00`);

        if (payDate === '' || Number.isNaN(parsedDate.getTime())) {
          return { is_valid: false, error: 'Select a valid pay date.' };
        }

        if (previousPayDate !== null && payDate <= previousPayDate) {
          return {
            is_valid: false,
            error: 'Pay date must be after the previous pay period.',
          };
        }

        return { is_valid: true };
      };

    return { validate_pay_date: validatePayDate };
  };
