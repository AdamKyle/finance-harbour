import React, { ChangeEvent, FormEvent, ReactNode, useState } from 'react';

import { useGoogleSocialAuth } from 'lib/authentication/api/hooks/use-google-social-auth';
import { useLogin } from 'lib/authentication/api/hooks/use-login';

import loginImage from 'assets/login-and-registration/finance-harbour-login.png';

import { navigateToRoute } from 'router/utils/navigate-to-route';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import Card from 'ui/cards/card';
import Input from 'ui/form-elements/input';

const Login = () => {
  const { error, loading, setRequestData } = useLogin({
    navigate_to_route: navigateToRoute,
  });
  const { redirectToGoogle } = useGoogleSocialAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const getErrorMessage = (
    fieldError?: string | string[]
  ): string | undefined => {
    if (!fieldError) {
      return undefined;
    }

    if (Array.isArray(fieldError)) {
      return fieldError.join(' ');
    }

    return fieldError;
  };

  const isSubmitDisabled = email === '' || password === '' || loading;
  const emailError = getErrorMessage(error?.email);
  const passwordError = getErrorMessage(error?.password);

  const handleChangeEmail = (event: ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value);
  };

  const handleChangePassword = (event: ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value);
  };

  const handleClickGoogleLogin = () => {
    redirectToGoogle();
  };

  const handleClickLoadingButton = () => undefined;

  const handleSubmitLogin = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (isSubmitDisabled) {
      return;
    }

    setRequestData({
      email,
      password,
    });
  };

  const renderSubmitButton = (): ReactNode => {
    if (!loading) {
      return (
        <Button
          additional_css="w-full md:w-auto"
          disabled={isSubmitDisabled}
          label="Sign in"
          type="submit"
          variant={ButtonVariant.PRIMARY}
        />
      );
    }

    return (
      <IconButton
        additional_css="w-full md:w-auto"
        aria_label="Signing in"
        disabled
        icon="fa-solid fa-arrows-rotate animate-spin"
        label="Signing in"
        on_click={handleClickLoadingButton}
        show_label
        variant={ButtonVariant.PRIMARY}
      />
    );
  };

  return (
    <main className="flex flex-1 items-start justify-center px-4 py-10 md:items-center md:px-6">
      <section
        aria-labelledby="login-title"
        className="flex w-full max-w-md flex-col gap-6"
      >
        <div className="flex items-center gap-4 text-left">
          <img
            alt=""
            aria-hidden="true"
            className="h-20 w-20 shrink-0 object-contain md:h-24 md:w-24"
            src={loginImage}
          />

          <div className="flex flex-col gap-2">
            <h1
              className="text-storm-dust-950 dark:text-storm-dust-50 text-3xl font-bold"
              id="login-title"
            >
              Sign in
            </h1>

            <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm leading-6">
              Sign in with your email and password to continue managing your
              budget.
            </p>
          </div>
        </div>

        <Card>
          <div className="flex flex-col gap-5">
            <IconButton
              additional_css="w-full justify-center"
              aria_label="Continue with Google"
              icon="fa-brands fa-google"
              label="Continue with Google"
              on_click={handleClickGoogleLogin}
              show_label
              variant={ButtonVariant.PRIMARY}
            />

            <form className="flex flex-col gap-5" onSubmit={handleSubmitLogin}>
              <Input
                autoComplete="email"
                error={emailError}
                has_error={emailError !== undefined}
                id="login-email"
                label="Email"
                name="email"
                onChange={handleChangeEmail}
                placeholder="you@example.com"
                required
                type="email"
                value={email}
              />

              <Input
                autoComplete="current-password"
                error={passwordError}
                has_error={passwordError !== undefined}
                id="login-password"
                label="Password"
                name="password"
                onChange={handleChangePassword}
                required
                type="password"
                value={password}
              />

              <div className="flex justify-end">{renderSubmitButton()}</div>
            </form>
          </div>
        </Card>
      </section>
    </main>
  );
};

export default Login;
