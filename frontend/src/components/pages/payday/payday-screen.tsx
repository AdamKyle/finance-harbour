import { useNavigate } from 'react-router';

import PaydayWizard from './components/payday-wizard';
import { usePaydayQueueContext } from './context/use-payday-queue-context';
import PaydayScreenProps from './types/payday-screen-props';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';
import { useEventSystem } from 'lib/event-system/hooks/use-event-system';

import { useMarkPaydayIncomplete } from 'components/pages/payday/api/hooks/use-mark-payday-incomplete';
import { usePaydayDetail } from 'components/pages/payday/api/hooks/use-payday-detail';
import { PaydayReconciliationStatus } from 'components/pages/payday/enums/payday-status';
import { PaydayEvent } from 'components/pages/payday/events/payday-event';
import { PaydayEventEmitterName } from 'components/pages/payday/events/payday-event-emitter-name';
import { PaydayEventMap } from 'components/pages/payday/events/payday-event-map';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { getPaydayRoute } from 'router/utils/get-payday-route';

import { Alert } from 'ui/alerts/alert';
import { AlertVariant } from 'ui/alerts/enums/alert-variant';
import Button from 'ui/buttons/button';
import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import SectionWithTitle from 'ui/sections/section-with-title';

const PaydayScreen = ({ period_id }: PaydayScreenProps) => {
  const navigate = useNavigate();
  const eventSystem = useEventSystem();
  const { authenticatedUser } = useAuthentication();
  const { queue, refresh: refreshQueue, dismiss } = usePaydayQueueContext();
  const { detail, loading, error, refresh } = usePaydayDetail({ period_id });
  const markIncompleteMutation = useMarkPaydayIncomplete({ period_id });
  const dashboardRouteState = { focus_pay_period_id: period_id };
  const canMarkIncomplete =
    detail !== null &&
    queue !== null &&
    detail.pay_period.pay_date < queue.effective_date &&
    [
      PaydayReconciliationStatus.NOT_STARTED,
      PaydayReconciliationStatus.IN_PROGRESS,
    ].includes(detail.pay_period.payday_reconciliation_status);

  const handleLeaveReview = () => {
    if (queue !== null && authenticatedUser !== null) {
      dismiss(authenticatedUser.id, queue.effective_date);
    }

    void navigate(NavigationRoutes.DASHBOARD, { state: dashboardRouteState });
  };

  const handleMarkIncomplete = async () => {
    const response = await markIncompleteMutation.mark_incomplete();

    if (response === null) {
      return;
    }

    eventSystem
      .fetchOrCreateEventEmitter<PaydayEventMap>(PaydayEventEmitterName.PAYDAY)
      .emit(PaydayEvent.BUDGET_PERIODS_RECALCULATED, {
        source_pay_period_id: period_id,
        affected_pay_period_ids: response.affected_pay_period_ids,
      });

    const refreshedQueue = await refreshQueue();

    if (
      refreshedQueue !== null &&
      refreshedQueue.oldest_unresolved_period !== null
    ) {
      void navigate(
        getPaydayRoute(refreshedQueue.oldest_unresolved_period.id),
        { replace: true }
      );

      return;
    }

    void navigate(NavigationRoutes.DASHBOARD, {
      replace: true,
      state: dashboardRouteState,
    });
  };

  const formatPayDate = (payDate: string) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC',
    }).format(new Date(`${payDate}T00:00:00Z`));
  };

  const renderIntroduction = () => {
    if (detail === null || queue === null) {
      return null;
    }

    if (queue.unresolved_count > 1) {
      return (
        <div>
          <h2 className="text-xl font-bold">
            Whoa, you&apos;ve been gone a while
          </h2>
          <p className="text-storm-dust-600 dark:text-storm-dust-300 mt-2">
            You have {queue.unresolved_count} paydays to review. Let&apos;s go
            through them one at a time and record what you remember.
          </p>
        </div>
      );
    }

    if (detail.pay_period.pay_date < queue.effective_date) {
      return (
        <div>
          <h2 className="text-xl font-bold">
            Let&apos;s catch up on {formatPayDate(detail.pay_period.pay_date)}
          </h2>
          <p className="text-storm-dust-600 dark:text-storm-dust-300 mt-2">
            This payday has passed. Let&apos;s record what you remember.
          </p>
        </div>
      );
    }

    return (
      <div>
        <h2 className="text-xl font-bold">It&apos;s payday</h2>
        <p className="text-storm-dust-600 dark:text-storm-dust-300 mt-2">
          Let&apos;s check what actually happened and take care of this pay
          period.
        </p>
      </div>
    );
  };

  const renderMarkIncomplete = () => {
    if (!canMarkIncomplete) {
      return null;
    }

    return (
      <Button
        label="Mark this payday incomplete"
        variant={ButtonVariant.WARNING}
        disabled={markIncompleteMutation.loading}
        on_click={() => void handleMarkIncomplete()}
      />
    );
  };

  const renderMarkIncompleteExplanation = () => {
    if (!canMarkIncomplete) {
      return null;
    }

    return (
      <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
        <strong>Mark Incomplete:</strong> Record anything you cannot remember as
        unknown and remove this payday from your catch-up queue. You can correct
        it later.
      </p>
    );
  };

  const renderError = () => {
    const displayedError = error ?? markIncompleteMutation.error;

    if (displayedError === null) {
      return null;
    }

    return <Alert variant={AlertVariant.DANGER}>{displayedError}</Alert>;
  };

  const renderLoading = () => {
    if (!loading || detail !== null) {
      return null;
    }

    return (
      <p role="status" className="text-storm-dust-600 dark:text-storm-dust-300">
        Loading payday review&hellip;
      </p>
    );
  };

  const renderWizard = () => {
    if (detail === null) {
      return null;
    }

    return (
      <PaydayWizard
        key={period_id}
        detail={detail}
        period_id={period_id}
        refresh_detail={refresh}
      />
    );
  };

  return (
    <SectionWithTitle
      title="Payday review"
      back_route={NavigationRoutes.DASHBOARD}
      back_state={dashboardRouteState}
      on_back={handleLeaveReview}
    >
      <div className="mx-auto w-full max-w-5xl space-y-6">
        {renderIntroduction()}
        {renderError()}
        {renderLoading()}
        {renderWizard()}
        <div className="border-storm-dust-200 dark:border-storm-dust-700 space-y-4 border-t pt-5">
          <div className="grid gap-4 sm:grid-cols-2">
            <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
              <strong>Skip:</strong> Leave this review unfinished and come back
              later.
            </p>
            {renderMarkIncompleteExplanation()}
          </div>
          <div className="grid gap-3 sm:grid-cols-2 [&>*]:w-full">
            <Button
              label="Skip for now"
              variant={ButtonVariant.Default}
              on_click={handleLeaveReview}
            />
            {renderMarkIncomplete()}
          </div>
        </div>
      </div>
    </SectionWithTitle>
  );
};

export default PaydayScreen;
