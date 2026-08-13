import clsx from 'clsx';
import { AnimatePresence, motion } from 'motion/react';
import { KeyboardEvent, useId, useRef, useState } from 'react';
import { NavLink } from 'react-router';

import AuthenticatedProfileMenuProps from './types/authenticated-profile-menu-props';

import { getAvatarById } from 'configuration/avatar-config';

import { UseLogout } from 'lib/authentication/api/hooks/use-logout';
import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { navigateToRoute } from 'router/utils/navigate-to-route';

const AuthenticatedProfileMenu = ({
  shouldReduceMotion,
}: AuthenticatedProfileMenuProps) => {
  const menuId = useId();
  const profileButtonRef = useRef<HTMLButtonElement | null>(null);
  const { authenticatedUser } = useAuthentication();
  const avatar = getAvatarById(authenticatedUser?.profile_photo ?? '');

  const { loading, logout } = UseLogout({
    navigate_to_route: navigateToRoute,
  });

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleCloseMenu = () => {
    setIsMenuOpen(false);
  };

  const handleCloseMenuAndRestoreFocus = () => {
    setIsMenuOpen(false);
    profileButtonRef.current?.focus();
  };

  const handleToggleMenu = () => {
    setIsMenuOpen((currentIsMenuOpen) => !currentIsMenuOpen);
  };

  const handleLogout = () => {
    handleCloseMenu();
    logout().catch(() => {});
  };

  const handleMenuKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== 'Escape') {
      return;
    }

    event.preventDefault();
    handleCloseMenuAndRestoreFocus();
  };

  const getProfileMenuLabel = () => {
    if (isMenuOpen) {
      return 'Close profile menu';
    }

    return 'Open profile menu';
  };

  const getMenuInitialAnimation = () => {
    if (shouldReduceMotion) {
      return false;
    }

    return { height: 0, opacity: 0, y: -8 };
  };

  const getMenuExitAnimation = () => {
    if (shouldReduceMotion) {
      return { opacity: 0 };
    }

    return { height: 0, opacity: 0, y: -8 };
  };

  const getMenuTransition = () => {
    if (shouldReduceMotion) {
      return { duration: 0 };
    }

    return { duration: 0.24, ease: 'easeOut' as const };
  };

  const getNavigationClassName = (isActive: boolean) => {
    const stateClassName = isActive
      ? 'bg-storm-dust-200 text-storm-dust-950 dark:bg-storm-dust-800 dark:text-storm-dust-50'
      : 'text-storm-dust-700 hover:bg-storm-dust-100 dark:text-storm-dust-200 dark:hover:bg-storm-dust-900';

    return clsx(
      'focus:ring-storm-dust-400 flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition focus:ring-2 focus:outline-hidden',
      stateClassName
    );
  };

  const getLogoutLabel = () => {
    if (loading) {
      return 'Logging out';
    }

    return 'Logout';
  };

  const renderAvatar = () => {
    if (avatar === null) {
      return (
        <i
          className="fa-solid fa-user text-storm-dust-600 dark:text-storm-dust-300 text-lg"
          aria-hidden="true"
        />
      );
    }

    return (
      <img
        src={avatar.src}
        alt=""
        className="h-9 w-9 rounded-full object-cover"
      />
    );
  };

  const renderMenu = () => {
    if (!isMenuOpen) {
      return null;
    }

    return (
      <motion.div
        key="authenticated-profile-menu"
        id={menuId}
        aria-label="Profile options"
        initial={getMenuInitialAnimation()}
        animate={{ height: 'auto', opacity: 1, y: 0 }}
        exit={getMenuExitAnimation()}
        transition={getMenuTransition()}
        onKeyDown={handleMenuKeyDown}
        className="border-storm-dust-200 bg-storm-dust-50 dark:border-storm-dust-800 dark:bg-storm-dust-950 absolute top-full right-0 mt-3 w-64 overflow-hidden rounded-2xl border p-2 shadow-lg"
      >
        <nav aria-label="Profile navigation">
          <ul className="space-y-1">
            <li>
              <NavLink
                to={NavigationRoutes.PROFILE}
                onClick={handleCloseMenu}
                className={({ isActive }) => getNavigationClassName(isActive)}
              >
                <i className="fa-solid fa-user" aria-hidden="true" />
                <span>Profile</span>
              </NavLink>
            </li>

            <li>
              <NavLink
                to={NavigationRoutes.SETTINGS}
                onClick={handleCloseMenu}
                className={({ isActive }) => getNavigationClassName(isActive)}
              >
                <i className="fa-solid fa-gear" aria-hidden="true" />
                <span>Settings</span>
              </NavLink>
            </li>

            <li>
              <NavLink
                to={NavigationRoutes.HELP}
                onClick={handleCloseMenu}
                className={({ isActive }) => getNavigationClassName(isActive)}
              >
                <i className="fa-solid fa-circle-question" aria-hidden="true" />
                <span>Help</span>
              </NavLink>
            </li>

            <li>
              <button
                type="button"
                disabled={loading}
                onClick={handleLogout}
                className={clsx(
                  'focus:ring-storm-dust-400 flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-medium transition focus:ring-2 focus:outline-hidden',
                  'text-storm-dust-700 hover:bg-storm-dust-100 dark:text-storm-dust-200 dark:hover:bg-storm-dust-900 disabled:cursor-not-allowed disabled:opacity-60'
                )}
              >
                <i
                  className="fa-solid fa-arrow-right-from-bracket"
                  aria-hidden="true"
                />
                <span>{getLogoutLabel()}</span>
              </button>
            </li>

            <li
              aria-hidden="true"
              className="bg-storm-dust-200 dark:bg-storm-dust-800 my-2 h-px"
            />

            <li>
              <NavLink
                to={NavigationRoutes.UPDATES}
                onClick={handleCloseMenu}
                className={({ isActive }) => getNavigationClassName(isActive)}
              >
                <i className="fa-solid fa-code-branch" aria-hidden="true" />
                <span>Version</span>
              </NavLink>
            </li>
          </ul>
        </nav>
      </motion.div>
    );
  };

  return (
    <div className="relative flex justify-end">
      <button
        ref={profileButtonRef}
        type="button"
        aria-label={getProfileMenuLabel()}
        aria-controls={menuId}
        aria-expanded={isMenuOpen}
        aria-haspopup="true"
        onClick={handleToggleMenu}
        className="border-storm-dust-400 bg-storm-dust-50 focus:ring-storm-dust-400 hover:bg-storm-dust-200 dark:border-storm-dust-600 dark:bg-storm-dust-900 dark:hover:bg-storm-dust-800 inline-flex h-11 w-11 cursor-pointer items-center justify-center rounded-full border transition focus:ring-2 focus:outline-hidden"
      >
        {renderAvatar()}
      </button>

      <AnimatePresence initial={false}>{renderMenu()}</AnimatePresence>
    </div>
  );
};

export default AuthenticatedProfileMenu;
