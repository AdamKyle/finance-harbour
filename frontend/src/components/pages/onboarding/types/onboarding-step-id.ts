export enum OnboardingStepId {
  PROFILE = 'profile',
  DEBTS = 'debts',
  INCOME = 'income',
  EXPENSES = 'expenses',
  CONCLUDE = 'conclude',
}

export const ONBOARDING_STEP_ORDER: OnboardingStepId[] = [
  OnboardingStepId.PROFILE,
  OnboardingStepId.DEBTS,
  OnboardingStepId.INCOME,
  OnboardingStepId.EXPENSES,
  OnboardingStepId.CONCLUDE,
];
