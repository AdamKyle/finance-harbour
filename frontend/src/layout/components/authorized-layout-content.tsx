import clsx from 'clsx';
import { type FocusEvent, type ReactNode, useState } from 'react';
import { Outlet } from 'react-router';

import {
  FHScreenHost,
  useFHScreenNavigation,
} from 'configuration/screen-manager/screen-manager-kit';
import {
  FHSidePeekHost,
  useFHSidePeekNavigation,
} from 'configuration/side-peek/side-peek-kit';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import ApplicationNavigation from 'components/authenticated-navigation/application-navigation';
import BaseAuthenticatedNavigation from 'components/authenticated-navigation/base-authenticated-navigation';
import PaydayAutoNavigator from 'components/pages/payday/payday-auto-navigator';

const AuthorizedLayoutContent = (): ReactNode => {
  const [isApplicationInputFocused, setIsApplicationInputFocused] =
    useState(false);
  const { stackDepth } = useFHScreenNavigation();
  const { stackDepth: sidePeekStackDepth } = useFHSidePeekNavigation();
  const { authenticatedUser } = useAuthentication();
  const hasActiveScreen = stackDepth > 0;
  const hasActiveSidePeek = sidePeekStackDepth > 0;
  const hasApplicationNavigation =
    authenticatedUser?.completed_onboarding === true;

  const getContentInert = () => {
    if (!hasActiveScreen) {
      return undefined;
    }

    return true;
  };

  const isEditableTarget = (target: EventTarget | null) => {
    if (target instanceof HTMLInputElement) {
      return !target.disabled && target.type !== 'hidden';
    }

    if (
      target instanceof HTMLTextAreaElement ||
      target instanceof HTMLSelectElement
    ) {
      return !target.disabled;
    }

    return target instanceof HTMLElement && target.isContentEditable;
  };

  const handleFocusCapture = (event: FocusEvent<HTMLDivElement>) => {
    setIsApplicationInputFocused(isEditableTarget(event.target));
  };

  const handleBlurCapture = (event: FocusEvent<HTMLDivElement>) => {
    setIsApplicationInputFocused(isEditableTarget(event.relatedTarget));
  };

  const renderApplicationNavigation = () => {
    if (!hasApplicationNavigation) {
      return null;
    }

    return (
      <ApplicationNavigation
        is_application_input_focused={isApplicationInputFocused}
      />
    );
  };

  return (
    <div className="bg-storm-dust-50 text-storm-dust-950 dark:bg-storm-dust-950 dark:text-storm-dust-50 flex min-h-dvh flex-col transition-colors duration-200">
      <div
        aria-hidden={hasActiveSidePeek}
        inert={hasActiveSidePeek || undefined}
      >
        <BaseAuthenticatedNavigation />
        <PaydayAutoNavigator />
      </div>
      <div
        className="relative flex min-w-0 flex-1"
        onFocusCapture={handleFocusCapture}
        onBlurCapture={handleBlurCapture}
        aria-hidden={hasActiveSidePeek}
        inert={hasActiveSidePeek || undefined}
      >
        {renderApplicationNavigation()}
        <div
          className={clsx({
            'absolute size-0 overflow-hidden': hasActiveScreen,
            'min-w-0 flex-1': !hasActiveScreen,
            'pb-[calc(6rem+env(safe-area-inset-bottom))] md:pb-0':
              hasApplicationNavigation && !hasActiveScreen,
          })}
          aria-hidden={hasActiveScreen}
          inert={getContentInert()}
        >
          <Outlet />
        </div>

        <div
          className={clsx({
            'size-0 overflow-hidden': !hasActiveScreen,
            'min-w-0 flex-1': hasActiveScreen,
            'pb-[calc(6rem+env(safe-area-inset-bottom))] md:pb-0':
              hasApplicationNavigation && hasActiveScreen,
          })}
        >
          <FHScreenHost />
        </div>
      </div>
      <FHSidePeekHost />
    </div>
  );
};

export default AuthorizedLayoutContent;
