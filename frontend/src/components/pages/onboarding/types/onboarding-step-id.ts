export enum OnboardingStepId {
  PROFILE = 'profile',
  DEBTS = 'debts',
  INCOME = 'income',
  EXPENSES = 'expenses',
  PAYMENT_SCHEDULE = 'payment_schedule',
  IMPORTANT_EXPENSES = 'important_expenses',
  LEFT_OVER_WARNING = 'left_over_warning',
  CONCLUDE = 'conclude',
}

export const ONBOARDING_STEP_ORDER: OnboardingStepId[] = [
  OnboardingStepId.PROFILE,
  OnboardingStepId.DEBTS,
  OnboardingStepId.INCOME,
  OnboardingStepId.EXPENSES,
  OnboardingStepId.PAYMENT_SCHEDULE,
  OnboardingStepId.IMPORTANT_EXPENSES,
  OnboardingStepId.LEFT_OVER_WARNING,
  OnboardingStepId.CONCLUDE,
];
