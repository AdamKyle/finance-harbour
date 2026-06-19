import React, { ReactNode, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router';

import { useGoogleSocialAuthCallback } from 'lib/authentication/api/hooks/use-google-social-auth-callback';

import { navigateToRoute } from 'router/utils/navigate-to-route';

import Card from 'ui/cards/card';

const GoogleAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const hasSubmittedRequest = useRef(false);

  const code = searchParams.get('code');

  const { error, loading, setRequestData } = useGoogleSocialAuthCallback({
    navigate_to_route: navigateToRoute,
  });

  const isAuthenticating = code !== null && !error;

  useEffect(() => {
    if (!code || hasSubmittedRequest.current) {
      return;
    }

    hasSubmittedRequest.current = true;

    setRequestData({
      code,
    });
  }, [code, setRequestData]);

  const getErrorMessage = (fieldError?: string | string[]): string | null => {
    if (!fieldError) {
      return null;
    }

    if (Array.isArray(fieldError)) {
      return fieldError.join(' ');
    }

    return fieldError;
  };

  const getGoogleAuthErrorMessage = (): string | null => {
    if (!code) {
      return 'Google did not return an authorization code. Please try signing in again.';
    }

    if (!error) {
      return null;
    }

    if (error.email) {
      return 'An account already exists with this email. Please sign in with your email and password.';
    }

    return (
      getErrorMessage(error.non_field_errors) ||
      getErrorMessage(error.detail) ||
      'Google sign in failed. Please try signing in again.'
    );
  };

  const getStatusTitle = (): string => {
    if (getGoogleAuthErrorMessage() !== null) {
      return 'Google sign in could not continue';
    }

    return 'Completing Google sign in';
  };

  const getStatusDescription = (): string => {
    const errorMessage = getGoogleAuthErrorMessage();

    if (errorMessage !== null) {
      return errorMessage;
    }

    return 'Please wait while Finance Harbour finishes signing you in with Google.';
  };

  const getStatusIconClassName = (): string => {
    if (loading || isAuthenticating) {
      return 'fa-solid fa-arrows-rotate animate-spin';
    }

    return 'fa-brands fa-google';
  };

  const renderStatusIcon = (): ReactNode => {
    if (getGoogleAuthErrorMessage() !== null) {
      return (
        <div className="bg-persian-plum-100 text-persian-plum-700 dark:bg-persian-plum-900 dark:text-persian-plum-100 flex h-14 w-14 items-center justify-center rounded-full">
          <i aria-hidden="true" className="fa-solid fa-triangle-exclamation" />
        </div>
      );
    }

    return (
      <div className="bg-blue-bell-100 text-blue-bell-700 dark:bg-blue-bell-900 dark:text-blue-bell-100 flex h-14 w-14 items-center justify-center rounded-full">
        <i aria-hidden="true" className={getStatusIconClassName()} />
      </div>
    );
  };

  return (
    <main className="flex min-h-0 flex-1 items-center justify-center overflow-hidden px-4 md:px-6">
      <section
        aria-labelledby="google-auth-callback-title"
        className="w-full max-w-md"
      >
        <Card additional_css="w-full">
          <div className="flex flex-col items-center gap-5 text-center">
            {renderStatusIcon()}

            <div className="flex flex-col gap-2">
              <h1
                className="text-storm-dust-950 dark:text-storm-dust-50 text-3xl font-bold"
                id="google-auth-callback-title"
              >
                {getStatusTitle()}
              </h1>

              <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm leading-6">
                {getStatusDescription()}
              </p>
            </div>
          </div>
        </Card>
      </section>
    </main>
  );
};

export default GoogleAuthCallback;
