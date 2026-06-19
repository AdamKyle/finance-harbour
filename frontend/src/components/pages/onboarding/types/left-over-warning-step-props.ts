import { LeftOverWarningStepFormState } from './left-over-warning-step-form-state';

export default interface LeftOverWarningStepProps {
  request: LeftOverWarningStepFormState;
  setRequest: (request: LeftOverWarningStepFormState) => void;
  error?: string;
}
