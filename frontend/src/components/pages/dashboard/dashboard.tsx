import { useReducedMotion } from 'motion/react';
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
} from 'react';
import { useLocation, useNavigate } from 'react-router';

import { BudgetLineItemDefinition } from './api/hooks/definitions/budget-line-item-definition';
import { useBudgetTimeline } from './api/hooks/use-budget-timeline';
import BudgetPayPeriodCard from './components/budget-pay-period-card';
import { useAddBillDashboardRefresh } from './hooks/use-add-bill-dashboard-refresh';
import { usePaydayDashboardRefresh } from './hooks/use-payday-dashboard-refresh';
import PrependMeasurement from './types/prepend-measurement';
import { getDashboardFocusPeriodId } from './utils/dashboard-route-state';

import { usePaydayQueueContext } from 'components/pages/payday/context/use-payday-queue-context';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const shouldReduceMotion = useReducedMotion();
  const { queue } = usePaydayQueueContext();
  const scrollRef = useRef<HTMLDivElement>(null);
  const focusTargetsRef = useRef(new Map<number, HTMLButtonElement>());
  const prependMeasurementRef = useRef<PrependMeasurement | null>(null);
  const focusedAnchorRef = useRef<number | null>(null);
  const routeFocusPeriodId = useMemo(
    () => getDashboardFocusPeriodId(location.state),
    [location.state]
  );
  const {
    periods,
    loading,
    loading_previous: loadingPrevious,
    loading_next: loadingNext,
    error,
    can_load_previous: canLoadPrevious,
    can_load_next: canLoadNext,
    anchor_period_id: defaultAnchorPeriodId,
    load_previous: loadPrevious,
    load_next: loadNext,
    refresh_loaded_pages: refreshLoadedPages,
  } = useBudgetTimeline({ anchor_period_id: routeFocusPeriodId });
  usePaydayDashboardRefresh({ refresh_dashboard: refreshLoadedPages });
  useAddBillDashboardRefresh({ refresh_dashboard: refreshLoadedPages });

  const sharedLineItems = useMemo(() => {
    const definitionsBySourceKey = new Map<string, BudgetLineItemDefinition>();

    periods.forEach((period) => {
      period.line_items.forEach((lineItem) => {
        if (!definitionsBySourceKey.has(lineItem.source_key)) {
          definitionsBySourceKey.set(lineItem.source_key, lineItem);
        }
      });
    });

    return Array.from(definitionsBySourceKey.values()).sort(
      (leftLineItem, rightLineItem) =>
        leftLineItem.display_order - rightLineItem.display_order ||
        leftLineItem.source_key.localeCompare(rightLineItem.source_key)
    );
  }, [periods]);
  const focusPeriodId = useMemo(
    () => routeFocusPeriodId ?? defaultAnchorPeriodId,
    [defaultAnchorPeriodId, routeFocusPeriodId]
  );
  const scrollBehavior = useMemo<ScrollBehavior>(() => {
    if (shouldReduceMotion === true) {
      return 'auto';
    }

    return 'smooth';
  }, [shouldReduceMotion]);

  const registerFocusTarget = useCallback(
    (periodId: number, element: HTMLButtonElement | null) => {
      if (element === null) {
        focusTargetsRef.current.delete(periodId);

        return;
      }

      focusTargetsRef.current.set(periodId, element);
    },
    []
  );

  useLayoutEffect(() => {
    const measurement = prependMeasurementRef.current;
    const scrollElement = scrollRef.current;

    if (measurement === null || scrollElement === null || loadingPrevious) {
      return;
    }

    scrollElement.scrollLeft =
      measurement.scroll_left +
      scrollElement.scrollWidth -
      measurement.scroll_width;
    prependMeasurementRef.current = null;
  }, [loadingPrevious, periods.length]);

  useEffect(() => {
    if (focusPeriodId === null || focusPeriodId === undefined || loading) {
      return;
    }

    const focusTarget = focusTargetsRef.current.get(focusPeriodId);

    if (
      focusTarget === undefined ||
      focusedAnchorRef.current === focusPeriodId
    ) {
      return;
    }

    focusTarget.scrollIntoView({
      behavior: scrollBehavior,
      block: 'center',
      inline: 'center',
    });
    focusTarget.focus({ preventScroll: true });
    focusedAnchorRef.current = focusPeriodId;

    if (routeFocusPeriodId !== undefined) {
      void navigate(location.pathname, { replace: true, state: null });
    }
  }, [
    focusPeriodId,
    loading,
    location.pathname,
    navigate,
    periods.length,
    routeFocusPeriodId,
    shouldReduceMotion,
    scrollBehavior,
  ]);

  const handleScroll = () => {
    const scrollElement = scrollRef.current;

    if (scrollElement === null) {
      return;
    }

    const nearStart = scrollElement.scrollLeft <= 200;
    const nearHorizontalEnd =
      scrollElement.scrollLeft + scrollElement.clientWidth >=
      scrollElement.scrollWidth - 200;
    if (nearStart && canLoadPrevious && !loadingPrevious) {
      prependMeasurementRef.current = {
        scroll_left: scrollElement.scrollLeft,
        scroll_width: scrollElement.scrollWidth,
      };
      void loadPrevious();

      return;
    }

    if (nearHorizontalEnd && canLoadNext && !loadingNext) {
      void loadNext();
    }
  };

  const handlePayDateSaved = async (periodId: number) => {
    await refreshLoadedPages();
    const focusTarget = focusTargetsRef.current.get(periodId);

    if (focusTarget === undefined) {
      return;
    }

    focusTarget.scrollIntoView({
      behavior: scrollBehavior,
      block: 'center',
      inline: 'center',
    });
    focusTarget.focus({ preventScroll: true });
  };

  const renderStatus = () => {
    if (loading && periods.length === 0) {
      return <p role="status">Loading your budget&hellip;</p>;
    }

    if (error !== null && periods.length === 0) {
      return <Alert variant={AlertVariant.DANGER}>{error.message}</Alert>;
    }

    if (periods.length === 0) {
      return <p>No budget data is available yet.</p>;
    }

    return null;
  };

  const renderLoading = () => {
    if (!loadingPrevious && !loadingNext) {
      return null;
    }

    return (
      <p role="status" className="text-center text-sm">
        Loading more periods&hellip;
      </p>
    );
  };

  const renderMobilePagination = () => {
    if (!canLoadPrevious && !canLoadNext) {
      return null;
    }

    const renderPreviousButton = () => {
      if (!canLoadPrevious) {
        return null;
      }

      return (
        <Button
          label="Load earlier pay periods"
          variant={ButtonVariant.Default}
          disabled={loadingPrevious}
          on_click={() => void loadPrevious()}
          additional_css="w-full"
        />
      );
    };

    const renderNextButton = () => {
      if (!canLoadNext) {
        return null;
      }

      return (
        <Button
          label="Load later pay periods"
          variant={ButtonVariant.Default}
          disabled={loadingNext}
          on_click={() => void loadNext()}
          additional_css="w-full"
        />
      );
    };

    return (
      <div className="grid gap-3 pb-4 md:hidden">
        {renderPreviousButton()}
        {renderNextButton()}
      </div>
    );
  };

  const renderCards = () => {
    if (periods.length === 0) {
      return null;
    }

    return (
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="grid grid-cols-1 items-stretch gap-5 pb-4 md:snap-x md:snap-mandatory md:auto-cols-[calc((100%_-_2rem)/3)] md:grid-flow-col md:grid-cols-none md:gap-4 md:overflow-x-auto md:overflow-y-hidden md:pb-8 md:motion-reduce:scroll-auto"
      >
        {periods.map((period) => {
          const handleFocusTarget = (element: HTMLButtonElement | null) => {
            registerFocusTarget(period.id, element);
          };

          return (
            <div key={period.id} className="h-full w-full md:snap-start">
              <BudgetPayPeriodCard
                period={period}
                line_items={sharedLineItems}
                on_saved={() => void refreshLoadedPages()}
                on_pay_date_saved={handlePayDateSaved}
                effective_payday_date={queue?.effective_date ?? null}
                register_focus_target={handleFocusTarget}
              />
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <main className="flex min-w-0 flex-1 flex-col px-4 py-8 md:px-6">
      <div className="w-full min-w-0">
        <h1 className="text-storm-dust-900 dark:text-storm-dust-50 mb-6 text-2xl font-bold">
          Your Budget
        </h1>
        {renderStatus()}
        {renderCards()}
        {renderMobilePagination()}
        {renderLoading()}
      </div>
    </main>
  );
};

export default Dashboard;
