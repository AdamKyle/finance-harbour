import { useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { useCompleteOnboarding } from 'components/pages/onboarding/api/hooks/use-complete-onboarding';

import { NavigationRoutes } from 'router/enums/navigation-routes';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IndeterminateProgressBar from 'ui/progress/indeterminate-progress-bar';

const BudgetBuildingScreen = () => {
  const navigate = useNavigate();
  const { setAuthenticatedUser } = useAuthentication();
  const { complete, loading, error } = useCompleteOnboarding();
  const hasStartedRef = useRef(false);
  const hasCompletedRef = useRef(false);

  const runCompletion = useCallback(async () => {
    if (hasCompletedRef.current) {
      return;
    }

    hasStartedRef.current = true;

    const result = await complete();

    if (result) {
      hasCompletedRef.current = true;

      setAuthenticatedUser((previousUser) => {
        if (previousUser === null) {
          return null;
        }

        return { ...previousUser, completed_onboarding: true };
      });

      void navigate(NavigationRoutes.DASHBOARD, { replace: true });
    }
  }, [complete, navigate, setAuthenticatedUser]);

  useEffect(() => {
    if (hasStartedRef.current) {
      return;
    }

    void runCompletion();
  }, [runCompletion]);

  const handleRetry = () => {
    if (loading) {
      return;
    }

    void runCompletion();
  };

  const renderProgress = () => {
    if (!loading) {
      return null;
    }

    return (
      <IndeterminateProgressBar label="Building your personalised budget" />
    );
  };

  const renderBuildingStatus = () => {
    if (!loading) {
      return null;
    }

    return (
      <div
        role="status"
        aria-live="polite"
        aria-busy="true"
        className="space-y-2 text-center"
      >
        <h1 className="text-storm-dust-900 dark:text-storm-dust-50 text-xl font-bold">
          We&apos;re building your budget
        </h1>
        <p className="text-storm-dust-500 dark:text-storm-dust-400 text-sm">
          Just hang tight while we prepare your next year of pay periods.
        </p>
        {renderProgress()}
      </div>
    );
  };

  const renderError = () => {
    if (!error || loading) {
      return null;
    }

    return (
      <div className="space-y-4">
        <Alert variant={AlertVariant.DANGER}>{error.message}</Alert>
        <Button
          on_click={handleRetry}
          variant={ButtonVariant.Default}
          label="Retry"
          additional_css="w-full"
        />
      </div>
    );
  };

  return (
    <main className="flex min-h-full flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm space-y-6">
        {renderBuildingStatus()}
        {renderError()}
      </div>
    </main>
  );
};

export default BudgetBuildingScreen;
