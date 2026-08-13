import { useReducedMotion } from 'motion/react';
import { useId, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router';

import BaseMobileNavigation from './base-mobile-navigation';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import mascotImage from 'assets/mascot/finance-harbour-mascot.png';

import AuthenticatedProfileMenu from 'components/authenticated-navigation/authenticated-profile-menu';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import type NavigationItemDefinition from 'router/public-routes/definitions/navigation-item-definition';
import { PUBLIC_NAVIGATION_ITEMS } from 'router/public-routes/public';
import { navigateToRoute } from 'router/utils/navigate-to-route';

import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import ToggleDarkMode from 'ui/dark-mode-toggle/toggle-dark-mode';

const BaseNavigation = () => {
  const navigate = useNavigate();
  const mobileMenuId = useId();
  const shouldReduceMotion = useReducedMotion();
  const { authenticatedUser, loading: isAuthenticationLoading } =
    useAuthentication();

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleCloseMenu = () => {
    setIsMenuOpen(false);
  };

  const handleToggleMenu = () => {
    setIsMenuOpen((currentIsMenuOpen) => !currentIsMenuOpen);
  };

  const handleLogin = () => {
    navigateToRoute(navigate, NavigationRoutes.LOGIN);
    handleCloseMenu();
  };

  const handleRegister = () => {
    navigateToRoute(navigate, NavigationRoutes.REGISTER);
    handleCloseMenu();
  };

  const getMobileMenuIconClassName = () => {
    if (isMenuOpen) {
      return 'fa-solid fa-xmark';
    }

    return 'fa-solid fa-bars';
  };

  const getMobileMenuLabel = () => {
    if (isMenuOpen) {
      return 'Close navigation menu';
    }

    return 'Open navigation menu';
  };

  const getNavigationLinkClassName = ({ isActive }: { isActive: boolean }) => {
    const baseClassName =
      'focus:ring-storm-dust-400 inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition focus:ring-2 focus:outline-hidden';

    if (isActive) {
      return `${baseClassName} bg-storm-dust-200 text-storm-dust-950 dark:bg-storm-dust-800 dark:text-storm-dust-50`;
    }

    return `${baseClassName} text-storm-dust-700 hover:bg-storm-dust-100 dark:text-storm-dust-200 dark:hover:bg-storm-dust-900`;
  };

  const renderNavigationLink = (navigationItem: NavigationItemDefinition) => {
    return (
      <NavLink
        key={navigationItem.href}
        to={navigationItem.href}
        onClick={handleCloseMenu}
        className={getNavigationLinkClassName}
      >
        {navigationItem.label}
      </NavLink>
    );
  };

  const renderDesktopAccountActions = () => {
    if (isAuthenticationLoading) {
      return (
        <span
          role="status"
          className="text-storm-dust-500 dark:text-storm-dust-400 text-sm"
        >
          Checking session&hellip;
        </span>
      );
    }

    if (authenticatedUser) {
      return (
        <AuthenticatedProfileMenu shouldReduceMotion={shouldReduceMotion} />
      );
    }

    return (
      <>
        <Button
          on_click={handleLogin}
          label="Login"
          variant={ButtonVariant.PRIMARY}
        />

        <Button
          on_click={handleRegister}
          label="Register"
          variant={ButtonVariant.SUCCESS}
        />
      </>
    );
  };

  return (
    <header className="border-storm-dust-200 bg-storm-dust-50/95 dark:border-storm-dust-800 dark:bg-storm-dust-950/95 sticky top-0 z-50 border-b backdrop-blur">
      <nav aria-label="Main navigation" className="mx-auto max-w-7xl px-6">
        <div className="grid min-h-20 grid-cols-[auto_1fr_auto] items-center gap-4">
          <Link
            to={NavigationRoutes.HOME}
            aria-label="Finance Harbour home"
            className="focus:ring-storm-dust-400 inline-flex items-center rounded-lg focus:ring-2 focus:outline-hidden"
          >
            <img
              src={mascotImage}
              alt=""
              aria-hidden="true"
              className="h-14 w-14 object-contain"
            />
          </Link>

          <div className="hidden justify-center md:flex">
            <div className="flex items-center gap-2">
              {PUBLIC_NAVIGATION_ITEMS.map(renderNavigationLink)}
            </div>
          </div>

          <div className="hidden items-center justify-end gap-3 md:flex">
            <ToggleDarkMode />

            {renderDesktopAccountActions()}
          </div>

          <IconButton
            on_click={handleToggleMenu}
            icon={getMobileMenuIconClassName()}
            label={getMobileMenuLabel()}
            aria_label={getMobileMenuLabel()}
            aria_expanded={isMenuOpen}
            aria_controls={mobileMenuId}
            variant={ButtonVariant.Default}
            additional_css="col-start-3 justify-self-end md:hidden"
          />
        </div>

        <BaseMobileNavigation
          isMenuOpen={isMenuOpen}
          mobileMenuId={mobileMenuId}
          navigationItems={PUBLIC_NAVIGATION_ITEMS}
          shouldReduceMotion={shouldReduceMotion}
          isAuthenticated={authenticatedUser !== null}
          isAuthenticationLoading={isAuthenticationLoading}
          onCloseMenu={handleCloseMenu}
          onLogin={handleLogin}
          onRegister={handleRegister}
        />
      </nav>
    </header>
  );
};

export default BaseNavigation;
