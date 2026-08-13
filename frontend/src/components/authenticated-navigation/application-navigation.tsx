import clsx from 'clsx';
import { MouseEvent } from 'react';
import { useLocation, useNavigate } from 'react-router';

import ApplicationNavigationProps from './types/application-navigation-props';

import { FinanceHarbourSidePeek } from 'configuration/side-peek/enums/finance-harbour-side-peek';
import { useFHSidePeekNavigation } from 'configuration/side-peek/side-peek-kit';

import { usePaydayQueueContext } from 'components/pages/payday/context/use-payday-queue-context';
import { PaydayReconciliationStatus } from 'components/pages/payday/enums/payday-status';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { getPaydayRoute } from 'router/utils/get-payday-route';
import { navigateToRoute } from 'router/utils/navigate-to-route';

import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';

const ApplicationNavigation = ({
  is_application_input_focused,
}: ApplicationNavigationProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { queue } = usePaydayQueueContext();
  const { push } = useFHSidePeekNavigation();

  const navigationButtonCss =
    'min-h-14 flex-1 flex-col justify-center gap-1 rounded-xl px-2 py-2 text-center text-xs md:w-full md:flex-none md:flex-row md:justify-start md:px-4 md:text-sm';

  const isRouteActive = (route: NavigationRoutes) => {
    return location.pathname === route;
  };

  const getVariant = (route: NavigationRoutes) => {
    if (!isRouteActive(route)) {
      return ButtonVariant.Default;
    }

    return ButtonVariant.PRIMARY;
  };

  const getAriaCurrent = (route: NavigationRoutes): 'page' | undefined => {
    if (!isRouteActive(route)) {
      return undefined;
    }

    return 'page';
  };

  const handleNavigate = (route: NavigationRoutes) => {
    navigateToRoute(navigate, route);
  };

  const handlePaydayNavigate = () => {
    if (queue?.oldest_unresolved_period === null || queue === null) {
      return;
    }

    void navigate(getPaydayRoute(queue.oldest_unresolved_period.id));
  };

  const handleAddBill = (event: MouseEvent<HTMLButtonElement>) => {
    push(FinanceHarbourSidePeek.ADD_BILL, undefined, event.currentTarget);
  };

  const renderPaydayAction = () => {
    if (queue === null || queue.unresolved_count === 0) {
      return null;
    }

    const getLabel = () => {
      if (queue.unresolved_count > 1) {
        return `Payday catch-up · ${queue.unresolved_count} periods`;
      }

      if (
        queue.oldest_unresolved_period?.payday_reconciliation_status ===
        PaydayReconciliationStatus.IN_PROGRESS
      ) {
        return 'Payday · Continue';
      }

      return 'Payday · Start review';
    };

    const label = getLabel();

    return (
      <IconButton
        icon="fa-solid fa-triangle-exclamation text-base"
        label={label}
        aria_label={`${label}. Oldest unresolved payday.`}
        show_label
        variant={ButtonVariant.WARNING}
        on_click={handlePaydayNavigate}
        additional_css={navigationButtonCss}
      />
    );
  };

  return (
    <nav
      aria-label="Budget application"
      className={clsx(
        'border-storm-dust-200 bg-storm-dust-50/95 dark:border-storm-dust-700 dark:bg-storm-dust-900/95 fixed inset-x-0 bottom-0 z-40 border-t px-2 pt-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] backdrop-blur md:sticky md:inset-x-auto md:top-24 md:bottom-auto md:z-10 md:ml-4 md:block md:w-56 md:self-start md:border-0 md:bg-transparent md:p-0 md:py-4 md:backdrop-blur-none dark:md:bg-transparent',
        { hidden: is_application_input_focused }
      )}
    >
      <div className="flex gap-2 md:flex-col md:gap-3">
        <IconButton
          icon="fa-solid fa-plus text-base"
          label="Add a bill"
          show_label
          variant={ButtonVariant.Default}
          on_click={handleAddBill}
          additional_css={navigationButtonCss}
        />
        <IconButton
          icon="fa-solid fa-wallet text-base"
          label="Track Spending"
          show_label
          variant={getVariant(NavigationRoutes.DASHBOARD)}
          aria_current={getAriaCurrent(NavigationRoutes.DASHBOARD)}
          on_click={() => handleNavigate(NavigationRoutes.DASHBOARD)}
          additional_css={navigationButtonCss}
        />
        <IconButton
          icon="fa-solid fa-calendar-days text-base"
          label="Plan future expenses"
          show_label
          variant={getVariant(NavigationRoutes.PLAN_FUTURE_EXPENSES)}
          aria_current={getAriaCurrent(NavigationRoutes.PLAN_FUTURE_EXPENSES)}
          on_click={() => handleNavigate(NavigationRoutes.PLAN_FUTURE_EXPENSES)}
          additional_css={navigationButtonCss}
        />
        <IconButton
          icon="fa-solid fa-chart-line text-base"
          label="Debt profiles"
          show_label
          variant={getVariant(NavigationRoutes.DEBT_PROFILES)}
          aria_current={getAriaCurrent(NavigationRoutes.DEBT_PROFILES)}
          on_click={() => handleNavigate(NavigationRoutes.DEBT_PROFILES)}
          additional_css={navigationButtonCss}
        />
        {renderPaydayAction()}
      </div>
    </nav>
  );
};

export default ApplicationNavigation;
