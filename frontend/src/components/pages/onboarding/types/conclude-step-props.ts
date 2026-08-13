import { DebtStepFormState } from './debt-step-form-state';
import { ExpenseStepFormState } from './expense-step-form-state';
import { ImportantExpensesStepFormState } from './important-expenses-step-form-state';
import { IncomeStepFormState } from './income-step-form-state';

export default interface ConcludeStepProps {
  debts: DebtStepFormState;
  expenses: ExpenseStepFormState;
  income: IncomeStepFormState;
  important_expenses: ImportantExpensesStepFormState;
}
