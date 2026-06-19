import React, { useMemo, useRef, useState } from 'react';

import ConcludeStep from './steps/conclude-step';
import DebtStep from './steps/debt-step';
import ExpenseStep from './steps/expense-step';
import IncomeStep from './steps/income-step';
import ProfileStep from './steps/profile-step';
import { DebtStepFormState } from './types/debt-step-form-state';
import { ExpenseStepFormState } from './types/expense-step-form-state';
import { IncomeStepFormState } from './types/income-step-form-state';
import {
  ONBOARDING_STEP_ORDER,
  OnboardingStepId,
} from './types/onboarding-step-id';
import { ProfileStepFormState } from './types/profile-step-form-state';
import { useScrollToTop } from '../../../util/hooks/use-scroll-to-top';

import { useCompleteOnboarding } from 'components/pages/onboarding/api/hooks/use-complete-onboarding';
import { useOnboardingProgress } from 'components/pages/onboarding/api/hooks/use-onboarding-progress';
import { useSaveDebtProfile } from 'components/pages/onboarding/api/hooks/use-save-debt-profile';
import { useSaveMonthlyExpense } from 'components/pages/onboarding/api/hooks/use-save-monthly-expense';
import { useSaveProfileOnboarding } from 'components/pages/onboarding/api/hooks/use-save-profile-onboarding';
import {
  mapDebtFormToApiRequest,
  mapExpenseFormToApiRequest,
  mapIncomeFormToApiRequest,
  mapProfileFormToApiRequest,
} from 'components/pages/onboarding/utils/onboarding-api-request-mappers';
import { buildOnboardingProgressFormData } from 'components/pages/onboarding/utils/onboarding-form-request';
import {
  DebtFieldErrorsDefinition,
  ExpenseFieldErrorsDefinition,
  IncomeFieldErrorsDefinition,
} from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { useOnboardingFormValidation } from 'components/pages/onboarding/validations/hooks/use-onboarding-form-validation';

import { navigateToRoute } from 'router/utils/navigate-to-route';

import FormWizard from 'ui/form-wizard/form-wizard';
import Step from 'ui/form-wizard/step';

const Onboarding = () => {
  const {
    progress,
    requestData,
    setRequestData,
    loading: progressLoading,
    saveProgress,
  } = useOnboardingProgress();
  const { save: saveProfile, loading: profileLoading } =
    useSaveProfileOnboarding();
  const { save: saveDebtProfile, loading: debtLoading } = useSaveDebtProfile();
  const { save: saveMonthlyExpense, loading: expenseLoading } =
    useSaveMonthlyExpense();
  const {
    complete,
    loading: completeLoading,
    error: completeError,
  } = useCompleteOnboarding({ navigate_to_route: navigateToRoute });
  const { validateDebtStep, validateIncomeStep, validateExpenseStep } =
    useOnboardingFormValidation();

  const [debtStepError, setDebtStepError] = useState('');
  const [debtFieldErrors, setDebtFieldErrors] = useState<
    DebtFieldErrorsDefinition[]
  >([]);
  const [incomeFieldErrors, setIncomeFieldErrors] =
    useState<IncomeFieldErrorsDefinition>({});
  const [expenseStepError, setExpenseStepError] = useState('');
  const [expenseFieldErrors, setExpenseFieldErrors] =
    useState<ExpenseFieldErrorsDefinition>({});
  const [saveError, setSaveError] = useState('');
  const formRef = useRef<HTMLElement>(null);
  const { scrollToTop } = useScrollToTop({
    targetRef: formRef,
    focusTarget: true,
  });

  const isLoading =
    profileLoading || debtLoading || expenseLoading || completeLoading;
  const initialIndex = useMemo(() => {
    if (!progress) {
      return 0;
    }

    const progressStepIndex = ONBOARDING_STEP_ORDER.indexOf(
      progress.current_step
    );

    return progressStepIndex >= 0 ? progressStepIndex : 0;
  }, [progress]);
  const saveApiError = saveError ? { message: saveError } : null;

  const handleProfileRequestChange = (profileRequest: ProfileStepFormState) => {
    setRequestData((currentRequest) => ({
      ...currentRequest,
      profile: profileRequest,
    }));
  };

  const handleDebtRequestChange = (debtRequest: DebtStepFormState) => {
    setRequestData((currentRequest) => ({
      ...currentRequest,
      debts: debtRequest,
    }));
  };

  const handleIncomeRequestChange = (incomeRequest: IncomeStepFormState) => {
    setRequestData((currentRequest) => ({
      ...currentRequest,
      income: incomeRequest,
    }));
  };

  const handleExpenseRequestChange = (expenseRequest: ExpenseStepFormState) => {
    setRequestData((currentRequest) => ({
      ...currentRequest,
      expenses: expenseRequest,
    }));
  };

  const handleRequestNext = async (stepIndex: number): Promise<boolean> => {
    const currentStep = ONBOARDING_STEP_ORDER[stepIndex];
    const nextStep =
      ONBOARDING_STEP_ORDER[stepIndex + 1] ?? ONBOARDING_STEP_ORDER[stepIndex];

    setSaveError('');

    if (currentStep === OnboardingStepId.PROFILE) {
      const saveResult = await saveProfile(
        mapProfileFormToApiRequest(requestData.profile)
      );

      if (!saveResult.ok) {
        setSaveError(saveResult.error ?? 'Failed to save profile');

        return false;
      }
    } else if (currentStep === OnboardingStepId.DEBTS) {
      const validationResult = validateDebtStep(requestData.debts);

      setDebtFieldErrors(validationResult.field_errors);
      setDebtStepError(validationResult.step_error);

      if (!validationResult.is_valid) {
        scrollToTop();

        return false;
      }

      const saveResult = await saveDebtProfile(
        mapDebtFormToApiRequest(requestData.debts)
      );

      if (!saveResult.ok) {
        setSaveError(saveResult.error ?? 'Failed to save debts');

        return false;
      }
    } else if (currentStep === OnboardingStepId.INCOME) {
      const validationResult = validateIncomeStep(requestData.income);

      setIncomeFieldErrors(validationResult.field_errors);

      if (!validationResult.is_valid) {
        scrollToTop();

        return false;
      }

      const saveResult = await saveDebtProfile(
        mapIncomeFormToApiRequest(requestData.income)
      );

      if (!saveResult.ok) {
        setSaveError(saveResult.error ?? 'Failed to save income');

        return false;
      }
    } else if (currentStep === OnboardingStepId.EXPENSES) {
      const validationResult = validateExpenseStep(requestData.expenses);

      setExpenseFieldErrors(validationResult.field_errors);
      setExpenseStepError(validationResult.step_error);

      if (!validationResult.is_valid) {
        scrollToTop();

        return false;
      }

      const saveResult = await saveMonthlyExpense(
        mapExpenseFormToApiRequest(requestData.expenses)
      );

      if (!saveResult.ok) {
        setSaveError(saveResult.error ?? 'Failed to save expenses');

        return false;
      }
    } else if (currentStep === OnboardingStepId.CONCLUDE) {
      return complete();
    }

    const completedSteps = [...(progress?.completed_steps ?? [])];

    if (!completedSteps.includes(currentStep)) {
      completedSteps.push(currentStep);
    }

    const progressResult = await saveProgress({
      current_step: nextStep,
      completed_steps: completedSteps,
      form_data: buildOnboardingProgressFormData(requestData),
    });

    if (!progressResult.ok) {
      setSaveError(
        progressResult.error ??
          'We could not save your onboarding progress. Please try again.'
      );

      return false;
    }

    return true;
  };

  if (progressLoading) {
    return (
      <main className="flex flex-1 items-center justify-center px-4 py-10">
        <p className="text-storm-dust-500 dark:text-storm-dust-400 text-sm">
          Loading...
        </p>
      </main>
    );
  }

  return (
    <main
      ref={formRef}
      aria-label="Onboarding form"
      className="flex flex-1 flex-col"
      tabIndex={-1}
    >
      <FormWizard
        total_steps={5}
        initial_index={initialIndex}
        name="Get started"
        is_loading={isLoading}
        on_request_next={handleRequestNext}
        form_error={completeError ?? saveApiError}
      >
        <Step step_title="Let's setup your profile!">
          <ProfileStep
            request={requestData.profile}
            setRequest={handleProfileRequestChange}
          />
        </Step>
        <Step step_title="Your debts">
          <DebtStep
            request={requestData.debts}
            setRequest={handleDebtRequestChange}
            stepError={debtStepError}
            fieldErrors={debtFieldErrors}
          />
        </Step>
        <Step step_title="Your income">
          <IncomeStep
            request={requestData.income}
            setRequest={handleIncomeRequestChange}
            fieldErrors={incomeFieldErrors}
          />
        </Step>
        <Step step_title="Your expenses">
          <ExpenseStep
            request={requestData.expenses}
            setRequest={handleExpenseRequestChange}
            stepError={expenseStepError}
            fieldErrors={expenseFieldErrors}
          />
        </Step>
        <Step step_title="All done">
          <ConcludeStep />
        </Step>
      </FormWizard>
    </main>
  );
};

export default Onboarding;
