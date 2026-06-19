import { DebtStepFormState } from './debt-step-form-state';
import { ExpenseStepFormState } from './expense-step-form-state';
import { IncomeStepFormState } from './income-step-form-state';
import { ProfileStepFormState } from './profile-step-form-state';

export interface OnboardingFormData {
  profile: ProfileStepFormState;
  debts: DebtStepFormState;
  income: IncomeStepFormState;
  expenses: ExpenseStepFormState;
}
