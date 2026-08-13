import { DebtStepFormState } from 'components/pages/onboarding/types/debt-step-form-state';
import { ExpenseStepFormState } from 'components/pages/onboarding/types/expense-step-form-state';
import { IncomeStepFormState } from 'components/pages/onboarding/types/income-step-form-state';
import { LeftOverWarningStepFormState } from 'components/pages/onboarding/types/left-over-warning-step-form-state';
import { ProfileStepFormState } from 'components/pages/onboarding/types/profile-step-form-state';
import {
  DebtFieldErrorsDefinition,
  ExpenseFieldErrorsDefinition,
  IncomeFieldErrorsDefinition,
  LeftOverWarningFieldErrorsDefinition,
  PaymentScheduleFieldErrorsDefinition,
  ProfileFieldErrorsDefinition,
} from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { OnboardingValidationResultDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-validation-result-definition';

export interface UseOnboardingFormValidationDefinition {
  validateProfileStep: (
    profileForm: ProfileStepFormState
  ) => OnboardingValidationResultDefinition<ProfileFieldErrorsDefinition>;
  validateDebtStep: (
    debtForm: DebtStepFormState
  ) => OnboardingValidationResultDefinition<DebtFieldErrorsDefinition[]>;
  validateIncomeStep: (
    incomeForm: IncomeStepFormState
  ) => OnboardingValidationResultDefinition<IncomeFieldErrorsDefinition>;
  validateExpenseStep: (
    expenseForm: ExpenseStepFormState
  ) => OnboardingValidationResultDefinition<ExpenseFieldErrorsDefinition>;
  validatePaymentScheduleStep: (
    debtForm: DebtStepFormState,
    expenseForm: ExpenseStepFormState,
    incomeForm: IncomeStepFormState
  ) => OnboardingValidationResultDefinition<PaymentScheduleFieldErrorsDefinition>;
  validateLeftOverWarningStep: (
    warningForm: LeftOverWarningStepFormState
  ) => OnboardingValidationResultDefinition<LeftOverWarningFieldErrorsDefinition>;
}
