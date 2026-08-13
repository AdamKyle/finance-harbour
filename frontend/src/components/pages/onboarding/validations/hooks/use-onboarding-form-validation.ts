import {
  dollarsToCents,
  validateDollarInput,
  validatePositiveDollarInput,
} from 'lib/money/money';

import { ExpensePaymentTiming } from 'components/pages/onboarding/enums/expense-payment-timing';
import { PaycheckPosition } from 'components/pages/onboarding/enums/paycheck-position';
import { UtilityType } from 'components/pages/onboarding/enums/utility-type';
import { PayPeriodType } from 'components/pages/onboarding/types/pay-period-type';
import {
  DebtFieldErrorsDefinition,
  ExpenseFieldErrorsDefinition,
  IncomeFieldErrorsDefinition,
  LeftOverWarningFieldErrorsDefinition,
  MiscExpenseFieldErrorsDefinition,
  PaymentScheduleFieldErrorsDefinition,
  ProfileFieldErrorsDefinition,
} from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { UseOnboardingFormValidationDefinition } from 'components/pages/onboarding/validations/hooks/definitions/use-onboarding-form-validation-definition';

export const useOnboardingFormValidation =
  (): UseOnboardingFormValidationDefinition => {
    const isPaycheckPositionInvalid = (
      position: PaycheckPosition,
      payPeriodType: PayPeriodType | ''
    ) => {
      if (payPeriodType === PayPeriodType.MONTHLY) {
        return position !== PaycheckPosition.FIRST;
      }

      if (payPeriodType === PayPeriodType.BIWEEKLY) {
        return (
          position !== PaycheckPosition.FIRST &&
          position !== PaycheckPosition.SECOND &&
          position !== PaycheckPosition.LAST
        );
      }

      return payPeriodType !== PayPeriodType.WEEKLY;
    };

    const isPaymentScheduleInvalid = (
      timing: ExpensePaymentTiming,
      position: PaycheckPosition,
      day: string,
      autoDeducted: boolean | null,
      payPeriodType: PayPeriodType | ''
    ) => {
      if (timing === ExpensePaymentTiming.EVERY_PAYCHECK) {
        return false;
      }

      if (timing === ExpensePaymentTiming.PAYCHECK_POSITION) {
        return isPaycheckPositionInvalid(position, payPeriodType);
      }

      const parsedDay = Number.parseInt(day, 10);

      return (
        !/^\d+$/.test(day) ||
        parsedDay < 1 ||
        parsedDay > 31 ||
        autoDeducted === null
      );
    };

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
          const debtErrors: DebtFieldErrorsDefinition = {};

          if (debtEntry.label.trim() === '') {
            debtErrors.label = 'Label is required';
          }

          const balanceValidation = validatePositiveDollarInput(
            debtEntry.current_balance_dollars,
            'Current balance'
          );
          const minimumValidation = validatePositiveDollarInput(
            debtEntry.minimum_payment_dollars,
            'Minimum payment'
          );
          const currentValidation = validatePositiveDollarInput(
            debtEntry.current_payment_dollars,
            'Current payment'
          );

          if (!balanceValidation.valid) {
            debtErrors.current_balance_dollars = balanceValidation.error;
          }

          if (!minimumValidation.valid) {
            debtErrors.minimum_payment_dollars = minimumValidation.error;
          }

          if (!currentValidation.valid) {
            debtErrors.current_payment_dollars = currentValidation.error;
          }

          return debtErrors;
        });
        const hasErrors = fieldErrors.some(
          (errors) => Object.keys(errors).length > 0
        );

        if (!hasErrors) {
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

        if (incomeForm.pay_period_type === '') {
          fieldErrors.pay_period_type = 'Select a pay period';
        }

        if (incomeForm.next_pay_date === '') {
          fieldErrors.next_pay_date = 'Select your next pay date.';
        } else {
          const parsedDate = new Date(`${incomeForm.next_pay_date}T12:00:00`);
          const today = new Date();
          today.setHours(0, 0, 0, 0);

          if (Number.isNaN(parsedDate.getTime())) {
            fieldErrors.next_pay_date = 'Enter a valid date.';
          } else if (parsedDate < today) {
            fieldErrors.next_pay_date =
              'Next pay date must not be in the past.';
          }
        }

        return {
          is_valid: Object.keys(fieldErrors).length === 0,
          step_error: '',
          field_errors: fieldErrors,
        };
      };

    const validateExpenseStep: UseOnboardingFormValidationDefinition['validateExpenseStep'] =
      (expenseForm) => {
        const fieldErrors: ExpenseFieldErrorsDefinition = {};

        const validateAmount = (
          fieldName: Exclude<
            keyof ExpenseFieldErrorsDefinition,
            'misc_expenses'
          >,
          value: string
        ) => {
          if (value === '') {
            return;
          }

          const validation = validateDollarInput(value);

          if (!validation.valid) {
            fieldErrors[fieldName] = validation.error;
          }
        };

        const isPositiveAmount = (value: string) => {
          return (
            value !== '' &&
            validateDollarInput(value).valid &&
            dollarsToCents(value) > 0
          );
        };

        if (
          expenseForm.utilities_dollars !== '' &&
          expenseForm.utility_type === ''
        ) {
          fieldErrors.utility_type = 'Select the type of utilities bill.';
        }

        if (
          expenseForm.utility_type === UtilityType.CUSTOM &&
          expenseForm.utility_custom_label.trim() === ''
        ) {
          fieldErrors.utility_custom_label = 'Enter a custom utility name.';
        }

        validateAmount(
          'rent_or_mortgage_dollars',
          expenseForm.rent_or_mortgage_dollars
        );
        validateAmount('utilities_dollars', expenseForm.utilities_dollars);
        validateAmount('food_dollars', expenseForm.food_dollars);

        if (!expenseForm.utilities_includes_internet) {
          validateAmount('internet_dollars', expenseForm.internet_dollars);
        }

        validateAmount('phone_dollars', expenseForm.phone_dollars);
        validateAmount('car_payment_dollars', expenseForm.car_payment_dollars);
        validateAmount('insurance_dollars', expenseForm.insurance_dollars);

        const miscErrors = expenseForm.misc_expenses.map((expense) => {
          const errors: MiscExpenseFieldErrorsDefinition = {};
          const hasLabel = expense.label.trim() !== '';
          const hasAmount = expense.amount_dollars.trim() !== '';

          if (!hasLabel && !hasAmount) {
            return errors;
          }

          if (!hasLabel) {
            errors.label = 'Enter a label, or remove this expense.';
          }

          if (!hasAmount) {
            errors.amount_dollars = 'Enter an amount, or remove this expense.';
          } else {
            const validation = validateDollarInput(expense.amount_dollars);

            if (!validation.valid) {
              errors.amount_dollars = validation.error;
            }
          }

          return errors;
        });

        if (miscErrors.some((errors) => Object.keys(errors).length > 0)) {
          fieldErrors.misc_expenses = miscErrors;
        }

        const hasPositiveCommonExpense =
          isPositiveAmount(expenseForm.rent_or_mortgage_dollars) ||
          isPositiveAmount(expenseForm.utilities_dollars) ||
          isPositiveAmount(expenseForm.food_dollars) ||
          (!expenseForm.utilities_includes_internet &&
            isPositiveAmount(expenseForm.internet_dollars)) ||
          isPositiveAmount(expenseForm.phone_dollars) ||
          isPositiveAmount(expenseForm.car_payment_dollars) ||
          isPositiveAmount(expenseForm.insurance_dollars);
        const hasPositiveMiscExpense = expenseForm.misc_expenses.some(
          (expense) =>
            expense.label.trim() !== '' &&
            isPositiveAmount(expense.amount_dollars)
        );

        if (Object.keys(fieldErrors).length > 0) {
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

        return { is_valid: true, step_error: '', field_errors: {} };
      };

    const validatePaymentScheduleStep: UseOnboardingFormValidationDefinition['validatePaymentScheduleStep'] =
      (debtForm, expenseForm, incomeForm) => {
        const fieldErrors: PaymentScheduleFieldErrorsDefinition = {};

        const validateSchedule = (
          sourceKey: string,
          amount: string,
          timing: ExpensePaymentTiming,
          paycheckPosition: PaycheckPosition,
          dayOfMonth: string,
          autoDeducted: boolean | null
        ) => {
          if (
            amount === '' ||
            !validateDollarInput(amount).valid ||
            dollarsToCents(amount) <= 0
          ) {
            return;
          }

          if (
            isPaymentScheduleInvalid(
              timing,
              paycheckPosition,
              dayOfMonth,
              autoDeducted,
              incomeForm.pay_period_type
            )
          ) {
            fieldErrors[sourceKey] = 'Complete this payment schedule.';
          }
        };

        validateSchedule(
          'rent_or_mortgage',
          expenseForm.rent_or_mortgage_dollars,
          expenseForm.payment_schedules.rent_or_mortgage.timing,
          expenseForm.payment_schedules.rent_or_mortgage.paycheck_position,
          expenseForm.payment_schedules.rent_or_mortgage.day_of_month,
          expenseForm.payment_schedules.rent_or_mortgage.auto_deducted
        );
        validateSchedule(
          'utilities',
          expenseForm.utilities_dollars,
          expenseForm.payment_schedules.utilities.timing,
          expenseForm.payment_schedules.utilities.paycheck_position,
          expenseForm.payment_schedules.utilities.day_of_month,
          expenseForm.payment_schedules.utilities.auto_deducted
        );
        validateSchedule(
          'food',
          expenseForm.food_dollars,
          expenseForm.payment_schedules.food.timing,
          expenseForm.payment_schedules.food.paycheck_position,
          expenseForm.payment_schedules.food.day_of_month,
          expenseForm.payment_schedules.food.auto_deducted
        );

        if (!expenseForm.utilities_includes_internet) {
          validateSchedule(
            'internet',
            expenseForm.internet_dollars,
            expenseForm.payment_schedules.internet.timing,
            expenseForm.payment_schedules.internet.paycheck_position,
            expenseForm.payment_schedules.internet.day_of_month,
            expenseForm.payment_schedules.internet.auto_deducted
          );
        }

        validateSchedule(
          'phone',
          expenseForm.phone_dollars,
          expenseForm.payment_schedules.phone.timing,
          expenseForm.payment_schedules.phone.paycheck_position,
          expenseForm.payment_schedules.phone.day_of_month,
          expenseForm.payment_schedules.phone.auto_deducted
        );
        validateSchedule(
          'car_payment',
          expenseForm.car_payment_dollars,
          expenseForm.payment_schedules.car_payment.timing,
          expenseForm.payment_schedules.car_payment.paycheck_position,
          expenseForm.payment_schedules.car_payment.day_of_month,
          expenseForm.payment_schedules.car_payment.auto_deducted
        );
        validateSchedule(
          'insurance',
          expenseForm.insurance_dollars,
          expenseForm.payment_schedules.insurance.timing,
          expenseForm.payment_schedules.insurance.paycheck_position,
          expenseForm.payment_schedules.insurance.day_of_month,
          expenseForm.payment_schedules.insurance.auto_deducted
        );

        expenseForm.misc_expenses.forEach((expense, index) => {
          validateSchedule(
            `misc:${index}`,
            expense.amount_dollars,
            expense.payment_schedule.timing,
            expense.payment_schedule.paycheck_position,
            expense.payment_schedule.day_of_month,
            expense.payment_schedule.auto_deducted
          );
        });
        debtForm.debts.forEach((debt, index) => {
          validateSchedule(
            `debt:${index}`,
            debt.current_payment_dollars,
            debt.payment_schedule.timing,
            debt.payment_schedule.paycheck_position,
            debt.payment_schedule.day_of_month,
            debt.payment_schedule.auto_deducted
          );
        });

        const isValid = Object.keys(fieldErrors).length === 0;
        let stepError = '';

        if (!isValid) {
          stepError = 'Complete the schedule for each payment.';
        }

        return {
          is_valid: isValid,
          step_error: stepError,
          field_errors: fieldErrors,
        };
      };

    const validateLeftOverWarningStep: UseOnboardingFormValidationDefinition['validateLeftOverWarningStep'] =
      (warningForm) => {
        const fieldErrors: LeftOverWarningFieldErrorsDefinition = {};
        const validation = validateDollarInput(
          warningForm.left_over_warning_amount_dollars
        );

        if (
          warningForm.left_over_warning_amount_dollars === '' ||
          !validation.valid
        ) {
          fieldErrors.left_over_warning_amount_dollars = validation.error;
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
      validatePaymentScheduleStep,
      validateLeftOverWarningStep,
    };
  };
