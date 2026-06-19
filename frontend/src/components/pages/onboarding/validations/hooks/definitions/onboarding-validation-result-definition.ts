export interface OnboardingValidationResultDefinition<FieldErrors> {
  is_valid: boolean;
  step_error: string;
  field_errors: FieldErrors;
}
