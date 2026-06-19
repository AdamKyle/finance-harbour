import { ExpenseStepFormState } from './expense-step-form-state';

import { ExpenseFieldErrorsDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';

export default interface ExpenseStepProps {
  request: ExpenseStepFormState;
  setRequest: (request: ExpenseStepFormState) => void;
  stepError?: string;
  fieldErrors?: ExpenseFieldErrorsDefinition;
}
