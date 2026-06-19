import { DebtStepFormState } from './debt-step-form-state';

import { DebtFieldErrorsDefinition } from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';

export default interface DebtStepProps {
  request: DebtStepFormState;
  setRequest: (request: DebtStepFormState) => void;
  stepError?: string;
  fieldErrors?: DebtFieldErrorsDefinition[];
}
