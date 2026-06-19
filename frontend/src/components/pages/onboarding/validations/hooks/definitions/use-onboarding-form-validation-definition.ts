import { DebtStepFormState } from 'components/pages/onboarding/types/debt-step-form-state';
import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import { IncomeStepFormState } from 'components/pages/onboarding/types/income-step-form-state';
import {
  DebtFieldErrorsDefinition,
  ExpenseFieldErrorsDefinition,
  IncomeFieldErrorsDefinition,
} from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { OnboardingValidationResultDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-validation-result-definition';

export interface UseOnboardingFormValidationDefinition {
  validateDebtStep: (
    debtForm: DebtStepFormState
  ) => OnboardingValidationResultDefinition<DebtFieldErrorsDefinition[]>;
  validateIncomeStep: (
    incomeForm: IncomeStepFormState
  ) => OnboardingValidationResultDefinition<IncomeFieldErrorsDefinition>;
  validateExpenseStep: (
    expenseForm: ExpenseStepFormState
  ) => OnboardingValidationResultDefinition<ExpenseFieldErrorsDefinition>;
}
