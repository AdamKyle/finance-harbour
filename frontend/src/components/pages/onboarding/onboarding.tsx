import React, { useEffect, useMemo, useRef, useState } from 'react';

import ConcludeStep from './steps/conclude-step';
import DebtStep from './steps/debt-step';
import ExpenseStep from './steps/expense-step';
import ImportantExpensesStep from './steps/important-expenses-step';
import IncomeStep from './steps/income-step';
import LeftOverWarningStep from './steps/left-over-warning-step';
import PaymentScheduleStep from './steps/payment-schedule-step';
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

import { FinanceHarbourScreen } from 'configuration/screen-manager/enums/finance-harbour-screen';
import { useFHScreenNavigation } from 'configuration/screen-manager/screen-manager-kit';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

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
  mapDebtSchedulesToApiRequest,
  mapExpenseSchedulesToApiRequest,
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
  PaymentScheduleFieldErrorsDefinition,
  ProfileFieldErrorsDefinition,
} from 'components/pages/onboarding/validations/hooks/definitions/onboarding-form-errors-definition';
import { useOnboardingFormValidation } from 'components/pages/onboarding/validations/hooks/use-onboarding-form-validation';

import FormWizard from 'ui/form-wizard/form-wizard';
import Step from 'ui/form-wizard/step';

const Onboarding = () => {
  const { setAuthenticatedUser } = useAuthentication();
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
    setPage: setImportantExpensesPage,
  } = useImportantExpenses();
  const { save: saveRequiredExpenses, loading: requiredExpensesLoading } =
    useSaveRequiredExpenses();
  const { save: saveLeftOverWarning, loading: warningThresholdLoading } =
    useSaveLeftOverWarningThreshold();
  const { resetTo } = useFHScreenNavigation();
  const {
    validateProfileStep,
    validateDebtStep,
    validateIncomeStep,
    validateExpenseStep,
    validatePaymentScheduleStep,
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
  const [paymentScheduleStepError, setPaymentScheduleStepError] = useState('');
  const [paymentScheduleFieldErrors, setPaymentScheduleFieldErrors] =
    useState<PaymentScheduleFieldErrorsDefinition>({});
  const [saveError, setSaveError] = useState('');
  const formRef = useRef<HTMLElement>(null);
  const { scrollToTop } = useScrollToTop({
    targetRef: formRef,
    focusTarget: true,
  });

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
  const initialIndex = useMemo(() => {
    if (!progress) {
      return 0;
    }

    const progressStepIndex = ONBOARDING_STEP_ORDER.indexOf(
      progress.current_step
    );

    if (progressStepIndex < 0) {
      return 0;
    }

    return progressStepIndex;
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

  const isLoading =
    profileLoading ||
    debtLoading ||
    expenseLoading ||
    requiredExpensesLoading ||
    warningThresholdLoading;
  let saveApiError = null;

  if (saveError !== '') {
    saveApiError = { message: saveError };
  }

  const getSaveError = (error: string | undefined, fallback: string) => {
    if (error === undefined) {
      return fallback;
    }

    return error;
  };

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
        setSaveError(getSaveError(saveResult.error, 'Failed to save profile'));

        return false;
      }

      if (saveResult.data) {
        const { profile_photo } = saveResult.data;

        setAuthenticatedUser((current) => {
          if (current === null) {
            return null;
          }

          return { ...current, profile_photo };
        });
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
        setSaveError(getSaveError(saveResult.error, 'Failed to save debts'));

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
        setSaveError(getSaveError(saveResult.error, 'Failed to save income'));

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
        setSaveError(getSaveError(saveResult.error, 'Failed to save expenses'));

        return false;
      }

      setImportantExpensesPage(1);
      setImportantExpensesRefresh((currentRefresh) => !currentRefresh);
    } else if (currentStep === OnboardingStepId.IMPORTANT_EXPENSES) {
      const candidateKeys = new Set(
        importantExpenseCards.map((expenseCard) => expenseCard.key)
      );
      const selectedCandidateKeys =
        requestData.important_expenses.selected_keys.filter((sourceKey) =>
          candidateKeys.has(sourceKey)
        );
      const saveResult = await saveRequiredExpenses({
        selected_keys: selectedCandidateKeys,
      });

      if (!saveResult.ok) {
        setSaveError(
          getSaveError(saveResult.error, 'Failed to save important expenses')
        );

        return false;
      }
    } else if (currentStep === OnboardingStepId.PAYMENT_SCHEDULE) {
      const validationResult = validatePaymentScheduleStep(
        requestData.debts,
        requestData.expenses,
        requestData.income
      );

      setPaymentScheduleFieldErrors(validationResult.field_errors);
      setPaymentScheduleStepError(validationResult.step_error);

      if (!validationResult.is_valid) {
        scrollToTop();

        return false;
      }

      const debtScheduleResult = await saveDebtProfile(
        mapDebtSchedulesToApiRequest(requestData.debts)
      );

      if (!debtScheduleResult.ok) {
        setSaveError(
          getSaveError(
            debtScheduleResult.error,
            'Failed to save debt schedules'
          )
        );

        return false;
      }

      const expenseScheduleResult = await saveMonthlyExpense(
        mapExpenseSchedulesToApiRequest(requestData.expenses)
      );

      if (!expenseScheduleResult.ok) {
        setSaveError(
          getSaveError(
            expenseScheduleResult.error,
            'Failed to save expense schedules'
          )
        );

        return false;
      }

      setImportantExpensesPage(1);
      setImportantExpensesRefresh((currentRefresh) => !currentRefresh);
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
        setSaveError(
          getSaveError(saveResult.error, 'Failed to save warning threshold')
        );

        return false;
      }
    }

    return true;
  };

  const handleRequestNext = async (stepIndex: number): Promise<boolean> => {
    const currentStep = ONBOARDING_STEP_ORDER[stepIndex];

    if (currentStep === OnboardingStepId.CONCLUDE) {
      setSaveError('');
      resetTo(FinanceHarbourScreen.BUDGET_BUILDING);
      return true;
    }

    const saved = await saveCurrentStep(stepIndex);

    if (!saved) {
      return false;
    }

    let completedSteps: OnboardingStepId[] = [];

    if (progress !== null) {
      completedSteps = [...progress.completed_steps];
    }

    if (!completedSteps.includes(currentStep)) {
      completedSteps.push(currentStep);
    }

    let candidateNextStep = ONBOARDING_STEP_ORDER[stepIndex];

    if (ONBOARDING_STEP_ORDER[stepIndex + 1] !== undefined) {
      candidateNextStep = ONBOARDING_STEP_ORDER[stepIndex + 1];
    }
    let existingCurrentStepIndex = -1;

    if (progress !== null) {
      existingCurrentStepIndex = ONBOARDING_STEP_ORDER.indexOf(
        progress.current_step
      );
    }

    const candidateNextStepIndex =
      ONBOARDING_STEP_ORDER.indexOf(candidateNextStep);
    let nextStep = candidateNextStep;

    if (
      candidateNextStepIndex <= existingCurrentStepIndex &&
      progress !== null
    ) {
      nextStep = progress.current_step;
    }

    const progressResult = await saveProgress({
      current_step: nextStep,
      completed_steps: completedSteps,
      form_data: buildOnboardingProgressFormData(requestData),
    });

    if (!progressResult.ok) {
      setSaveError(
        getSaveError(
          progressResult.error,
          'We could not save your onboarding progress. Please try again.'
        )
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

    let progressCurrentStep = ONBOARDING_STEP_ORDER[currentIndex];
    let progressCompletedSteps: OnboardingStepId[] = [];

    if (progress !== null) {
      progressCurrentStep = progress.current_step;
      progressCompletedSteps = progress.completed_steps;
    }

    const progressResult = await saveProgress({
      current_step: progressCurrentStep,
      completed_steps: progressCompletedSteps,
      form_data: buildOnboardingProgressFormData(requestData),
    });

    if (!progressResult.ok) {
      setSaveError(
        getSaveError(
          progressResult.error,
          'We could not save your onboarding progress. Please try again.'
        )
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
        total_steps={8}
        initial_index={initialIndex}
        name="Get started"
        is_loading={isLoading}
        on_request_next={handleRequestNext}
        on_request_step_change={handleRequestStepChange}
        form_error={saveApiError}
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
        <Step step_title="When do these payments happen?">
          <PaymentScheduleStep
            debts={requestData.debts}
            expenses={requestData.expenses}
            income={requestData.income}
            setDebts={handleDebtRequestChange}
            setExpenses={handleExpenseRequestChange}
            stepError={paymentScheduleStepError}
            fieldErrors={paymentScheduleFieldErrors}
          />
        </Step>
        <Step step_title="Select what's important">
          <ImportantExpensesStep
            request={requestData.important_expenses}
            setRequest={handleImportantExpensesRequestChange}
            cards={importantExpenseCards}
            loading={importantExpensesLoading}
            is_loading_more={importantExpensesLoadingMore}
            can_load_more={canLoadMoreImportantExpenses}
            on_load_more={() => {
              loadMoreImportantExpenses();
            }}
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
          <ConcludeStep
            debts={requestData.debts}
            expenses={requestData.expenses}
            income={requestData.income}
            important_expenses={requestData.important_expenses}
          />
        </Step>
      </FormWizard>
    </main>
  );
};

export default Onboarding;
