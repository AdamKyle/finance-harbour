import { DebtStepFormState } from './debt-step-form-state';
import { ExpenseStepFormState } from './expense-step-form-state';
import { ImportantExpensesStepFormState } from './important-expenses-step-form-state';
import { IncomeStepFormState } from './income-step-form-state';
import { LeftOverWarningStepFormState } from './left-over-warning-step-form-state';
import { ProfileStepFormState } from './profile-step-form-state';

export interface OnboardingFormData {
  profile: ProfileStepFormState;
  debts: DebtStepFormState;
  income: IncomeStepFormState;
  expenses: ExpenseStepFormState;
  important_expenses: ImportantExpensesStepFormState;
  left_over_warning: LeftOverWarningStepFormState;
}
