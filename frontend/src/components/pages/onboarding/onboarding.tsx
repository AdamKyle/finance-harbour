import React, { useEffect, useMemo, useRef, useState } from 'react';

import ConcludeStep from './steps/conclude-step';
import DebtStep from './steps/debt-step';
import ExpenseStep from './steps/expense-step';
import ImportantExpensesStep from './steps/important-expenses-step';
import IncomeStep from './steps/income-step';
import LeftOverWarningStep from './steps/left-over-warning-step';
import ProfileStep from './steps/profile-step';
import { DebtStepFormState } from './types/debt-step-form-state';
import { ExpenseStepFormState } from './types/expense-step-form-state';
import { ImportantExpensesStepFormState } from './types/important-expenses-step-form-state';
import { IncomeStepFormState } from './types/income-step-form-state';
import { LeftOverWarningStepFormState } from './types/left-over-warning-step-form-state';
import {
  ONBOARDING_STEP_ORDER,
  OnboardingStepId,
} from './types/onboarding-step-id';
import { ProfileStepFormState } from './types/profile-step-form-state';
import { useScrollToTop } from '../../../util/hooks/use-scroll-to-top';

import { useCompleteOnboarding } from 'components/pages/onboarding/api/hooks/use-complete-onboarding';
import { useImportantExpenses } from 'components/pages/onboarding/api/hooks/use-important-expenses';
import { useOnboardingProgress } from 'components/pages/onboarding/api/hooks/use-onboarding-progress';
import { useSaveDebtProfile } from 'components/pages/onboarding/api/hooks/use-save-debt-profile';
import { useSaveLeftOverWarningThreshold } from 'components/pages/onboarding/api/hooks/use-save-left-over-warning-threshold';
import { useSaveMonthlyExpense } from 'components/pages/onboarding/api/hooks/use-save-monthly-expense';
import { useSaveProfileOnboarding } from 'components/pages/onboarding/api/hooks/use-save-profile-onboarding';
import { useSaveRequiredExpenses } from 'components/pages/onboarding/api/hooks/use-save-required-expenses';
import {
  mapDebtFormToApiRequest,
  mapExpenseFormToApiRequest,
  mapIncomeFormToApiRequest,
  mapLeftOverWarningFormToApiRequest,
  mapProfileFormToApiRequest,
} from 'components/pages/onboarding/utils/onboarding-api-request-mappers';
import { buildOnboardingProgressFormData } from 'components/pages/onboarding/utils/onboarding-form-request';
import {
  DebtFieldErrorsDefinition,
  ExpenseFieldErrorsDefinition,
  IncomeFieldErrorsDefinition,
  LeftOverWarningFieldErrorsDefinition,
  ProfileFieldErrorsDefinition,
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
    data: importantExpenseCards,
    loading: importantExpensesLoading,
    isLoadingMore: importantExpensesLoadingMore,
    canLoadMore: canLoadMoreImportantExpenses,
    onEndReached: loadMoreImportantExpenses,
    setRefresh: setImportantExpensesRefresh,
  } = useImportantExpenses();
  const { save: saveRequiredExpenses, loading: requiredExpensesLoading } =
    useSaveRequiredExpenses();
  const { save: saveLeftOverWarning, loading: warningThresholdLoading } =
    useSaveLeftOverWarningThreshold();
  const {
    complete,
    loading: completeLoading,
    error: completeError,
  } = useCompleteOnboarding({ navigate_to_route: navigateToRoute });
  const {
    validateProfileStep,
    validateDebtStep,
    validateIncomeStep,
    validateExpenseStep,
    validateLeftOverWarningStep,
  } = useOnboardingFormValidation();

  const [profileFieldErrors, setProfileFieldErrors] =
    useState<ProfileFieldErrorsDefinition>({});
  const [debtStepError, setDebtStepError] = useState('');
  const [debtFieldErrors, setDebtFieldErrors] = useState<
    DebtFieldErrorsDefinition[]
  >([]);
  const [incomeFieldErrors, setIncomeFieldErrors] =
    useState<IncomeFieldErrorsDefinition>({});
  const [expenseStepError, setExpenseStepError] = useState('');
  const [expenseFieldErrors, setExpenseFieldErrors] =
    useState<ExpenseFieldErrorsDefinition>({});
  const [warningFieldErrors, setWarningFieldErrors] =
    useState<LeftOverWarningFieldErrorsDefinition>({});
  const [saveError, setSaveError] = useState('');
  const formRef = useRef<HTMLElement>(null);
  const { scrollToTop } = useScrollToTop({
    targetRef: formRef,
    focusTarget: true,
  });

  const isLoading =
    profileLoading ||
    debtLoading ||
    expenseLoading ||
    requiredExpensesLoading ||
    warningThresholdLoading ||
    completeLoading;
  const initialIndex = useMemo(() => {
    if (!progress) {
      return 0;
    }

    const progressStepIndex = ONBOARDING_STEP_ORDER.indexOf(
      progress.current_step
    );

    return progressStepIndex >= 0 ? progressStepIndex : 0;
  }, [progress]);
  const available_step_indexes = useMemo(() => {
    if (!progress) {
      return [0];
    }

    return ONBOARDING_STEP_ORDER.reduce<number[]>((acc, step_id, index) => {
      if (
        progress.completed_steps.includes(step_id) ||
        step_id === progress.current_step
      ) {
        acc.push(index);
      }

      return acc;
    }, []);
  }, [progress]);
  const saveApiError = saveError ? { message: saveError } : null;

  useEffect(() => {
    if (requestData.important_expenses.selected_keys.length > 0) {
      return;
    }

    const selectedKeys = importantExpenseCards
      .filter((card) => card.selected)
      .map((card) => card.key);

    if (selectedKeys.length === 0) {
      return;
    }

    setRequestData((currentRequest) => ({
      ...currentRequest,
      important_expenses: {
        selected_keys: selectedKeys,
      },
    }));
  }, [
    importantExpenseCards,
    requestData.important_expenses.selected_keys.length,
    setRequestData,
  ]);

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

  const handleImportantExpensesRequestChange = (
    importantExpensesRequest: ImportantExpensesStepFormState
  ) => {
    setRequestData((currentRequest) => ({
      ...currentRequest,
      important_expenses: importantExpensesRequest,
    }));
  };

  const handleLeftOverWarningRequestChange = (
    warningRequest: LeftOverWarningStepFormState
  ) => {
    setRequestData((currentRequest) => ({
      ...currentRequest,
      left_over_warning: warningRequest,
    }));
  };

  const saveCurrentStep = async (stepIndex: number): Promise<boolean> => {
    const currentStep = ONBOARDING_STEP_ORDER[stepIndex];

    setSaveError('');

    if (currentStep === OnboardingStepId.PROFILE) {
      const validationResult = validateProfileStep(requestData.profile);

      setProfileFieldErrors(validationResult.field_errors);

      if (!validationResult.is_valid) {
        scrollToTop();

        return false;
      }

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

      setImportantExpensesRefresh((currentRefresh) => !currentRefresh);
    } else if (currentStep === OnboardingStepId.IMPORTANT_EXPENSES) {
      const saveResult = await saveRequiredExpenses(
        requestData.important_expenses
      );

      if (!saveResult.ok) {
        setSaveError(saveResult.error ?? 'Failed to save important expenses');

        return false;
      }
    } else if (currentStep === OnboardingStepId.LEFT_OVER_WARNING) {
      const validationResult = validateLeftOverWarningStep(
        requestData.left_over_warning
      );

      setWarningFieldErrors(validationResult.field_errors);

      if (!validationResult.is_valid) {
        scrollToTop();

        return false;
      }

      const saveResult = await saveLeftOverWarning(
        mapLeftOverWarningFormToApiRequest(requestData.left_over_warning)
      );

      if (!saveResult.ok) {
        setSaveError(saveResult.error ?? 'Failed to save warning threshold');

        return false;
      }
    }

    return true;
  };

  const handleRequestNext = async (stepIndex: number): Promise<boolean> => {
    const currentStep = ONBOARDING_STEP_ORDER[stepIndex];

    if (currentStep === OnboardingStepId.CONCLUDE) {
      setSaveError('');

      return complete();
    }

    const saved = await saveCurrentStep(stepIndex);

    if (!saved) {
      return false;
    }

    const completedSteps = [...(progress?.completed_steps ?? [])];

    if (!completedSteps.includes(currentStep)) {
      completedSteps.push(currentStep);
    }

    const candidateNextStep =
      ONBOARDING_STEP_ORDER[stepIndex + 1] ?? ONBOARDING_STEP_ORDER[stepIndex];
    const existingCurrentStepIndex = progress
      ? ONBOARDING_STEP_ORDER.indexOf(progress.current_step)
      : -1;
    const candidateNextStepIndex =
      ONBOARDING_STEP_ORDER.indexOf(candidateNextStep);
    const nextStep =
      candidateNextStepIndex > existingCurrentStepIndex
        ? candidateNextStep
        : (progress?.current_step ?? candidateNextStep);

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

  const handleRequestStepChange = async (
    currentIndex: number,
    _targetIndex: number
  ): Promise<boolean> => {
    const currentStep = ONBOARDING_STEP_ORDER[currentIndex];

    if (currentStep !== OnboardingStepId.CONCLUDE) {
      const saved = await saveCurrentStep(currentIndex);

      if (!saved) {
        return false;
      }
    } else {
      setSaveError('');
    }

    const progressResult = await saveProgress({
      current_step:
        progress?.current_step ?? ONBOARDING_STEP_ORDER[currentIndex],
      completed_steps: progress?.completed_steps ?? [],
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
        total_steps={7}
        initial_index={initialIndex}
        name="Get started"
        is_loading={isLoading}
        on_request_next={handleRequestNext}
        on_request_step_change={handleRequestStepChange}
        form_error={completeError ?? saveApiError}
        available_step_indexes={available_step_indexes}
      >
        <Step step_title="Let's setup your profile!">
          <ProfileStep
            request={requestData.profile}
            setRequest={handleProfileRequestChange}
            error={profileFieldErrors.nickname}
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
        <Step step_title="Select whats important">
          <ImportantExpensesStep
            request={requestData.important_expenses}
            setRequest={handleImportantExpensesRequestChange}
            cards={importantExpenseCards}
            loading={importantExpensesLoading}
            is_loading_more={importantExpensesLoadingMore}
            can_load_more={canLoadMoreImportantExpenses}
            on_load_more={loadMoreImportantExpenses}
          />
        </Step>
        <Step step_title="Left over warning threshold">
          <LeftOverWarningStep
            request={requestData.left_over_warning}
            setRequest={handleLeftOverWarningRequestChange}
            error={warningFieldErrors.left_over_warning_amount_dollars}
          />
        </Step>
        <Step step_title="Finish" show_title={false}>
          <ConcludeStep />
        </Step>
      </FormWizard>
    </main>
  );
};

export default Onboarding;
