import { IncomeStepFormState } from './income-step-form-state';

import { IncomeFieldErrorsDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';

export default interface IncomeStepProps {
  request: IncomeStepFormState;
  setRequest: (request: IncomeStepFormState) => void;
  fieldErrors?: IncomeFieldErrorsDefinition;
}
