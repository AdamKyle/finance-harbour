import { DebtStepFormState } from './debt-step-form-state';
import { ExpenseStepFormState } from './expense-step-form-state';
import { IncomeStepFormState } from './income-step-form-state';

import { PaymentScheduleFieldErrorsDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';

export default interface PaymentScheduleStepProps {
  debts: DebtStepFormState;
  expenses: ExpenseStepFormState;
  income: IncomeStepFormState;
  setDebts: (request: DebtStepFormState) => void;
  setExpenses: (request: ExpenseStepFormState) => void;
  stepError?: string;
  fieldErrors?: PaymentScheduleFieldErrorsDefinition;
}
