import { ProfileStepFormState } from './profile-step-form-state';

export default interface ProfileStepProps {
  request: ProfileStepFormState;
  setRequest: (request: ProfileStepFormState) => void;
}
