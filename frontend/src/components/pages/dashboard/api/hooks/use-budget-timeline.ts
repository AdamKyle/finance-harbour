import { AxiosError } from 'axios';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { BudgetPayPeriodDefinition } from './definitions/budget-pay-period-definition';
import BudgetTimelineResponseDefinition from './definitions/budget-timeline-response-definition';
import UseBudgetTimelineDefinition from './definitions/use-budget-timeline-definition';
import UseBudgetTimelineParamsDefinition from './definitions/use-budget-timeline-params-definition';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';
import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';

import { BudgetApiUrls } from 'components/pages/dashboard/api/enums/budget-api-urls';

export const useBudgetTimeline = ({
  anchor_period_id,
}: UseBudgetTimelineParamsDefinition): UseBudgetTimelineDefinition => {
  const { apiHandler, getUrl } = useApiHandler();
  const [pages, setPages] = useState<Map<number, BudgetPayPeriodDefinition[]>>(
    new Map()
  );
  const [loading, setLoading] = useState(true);
  const [loadingPrevious, setLoadingPrevious] = useState(false);
  const [loadingNext, setLoadingNext] = useState(false);
  const [error, setError] = useState<AxiosErrorDefinition | null>(null);
  const [canLoadPrevious, setCanLoadPrevious] = useState(false);
  const [canLoadNext, setCanLoadNext] = useState(false);
  const [resolvedAnchorPeriodId, setResolvedAnchorPeriodId] = useState<
    number | null
  >(null);
  const minimumPageRef = useRef<number | null>(null);
  const maximumPageRef = useRef<number | null>(null);
  const requestInFlightRef = useRef(false);

  const url = getUrl(BudgetApiUrls.BUDGET);
  const periods = useMemo(
    () =>
      [...pages.entries()]
        .sort(([leftPage], [rightPage]) => leftPage - rightPage)
        .flatMap(([, pagePeriods]) => pagePeriods),
    [pages]
  );

  const setRequestError = useCallback((requestError: unknown) => {
    if (requestError instanceof AxiosError) {
      setError({ message: requestError.message });

      return;
    }

    setError({ message: 'We could not load your budget. Please try again.' });
  }, []);

  const requestPage = useCallback(
    async (page?: number, requestedAnchorPeriodId?: number) => {
      return apiHandler.get<
        BudgetTimelineResponseDefinition,
        { page?: number; anchor_period_id?: number }
      >(url, {
        params: {
          page,
          anchor_period_id: requestedAnchorPeriodId,
        },
      });
    },
    [apiHandler, url]
  );

  const applyResponse = useCallback(
    (response: BudgetTimelineResponseDefinition) => {
      const responsePage = response.meta.pagination.current_page;
      setPages((currentPages) => {
        const nextPages = new Map(currentPages);
        nextPages.set(responsePage, response.data);

        return nextPages;
      });
      minimumPageRef.current = Math.min(
        minimumPageRef.current ?? responsePage,
        responsePage
      );
      maximumPageRef.current = Math.max(
        maximumPageRef.current ?? responsePage,
        responsePage
      );
      setCanLoadPrevious(response.meta.can_load_previous);
      setCanLoadNext(response.meta.can_load_more);
      setResolvedAnchorPeriodId(response.meta.anchor_period_id);
    },
    []
  );

  const loadPrevious = useCallback(async () => {
    const minimumPage = minimumPageRef.current;

    if (
      requestInFlightRef.current ||
      !canLoadPrevious ||
      minimumPage === null
    ) {
      return;
    }

    requestInFlightRef.current = true;
    setLoadingPrevious(true);
    setError(null);

    try {
      applyResponse(await requestPage(minimumPage - 1));
    } catch (requestError) {
      setRequestError(requestError);
    } finally {
      requestInFlightRef.current = false;
      setLoadingPrevious(false);
    }
  }, [applyResponse, canLoadPrevious, requestPage, setRequestError]);

  const loadNext = useCallback(async () => {
    const maximumPage = maximumPageRef.current;

    if (requestInFlightRef.current || !canLoadNext || maximumPage === null) {
      return;
    }

    requestInFlightRef.current = true;
    setLoadingNext(true);
    setError(null);

    try {
      applyResponse(await requestPage(maximumPage + 1));
    } catch (requestError) {
      setRequestError(requestError);
    } finally {
      requestInFlightRef.current = false;
      setLoadingNext(false);
    }
  }, [applyResponse, canLoadNext, requestPage, setRequestError]);

  const refreshLoadedPages = useCallback(async () => {
    const loadedPageNumbers = [...pages.keys()];

    if (loadedPageNumbers.length === 0) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const responses = await Promise.all(
        loadedPageNumbers.map((pageNumber) => requestPage(pageNumber))
      );
      responses.forEach(applyResponse);
    } catch (requestError) {
      setRequestError(requestError);
    } finally {
      setLoading(false);
    }
  }, [applyResponse, pages, requestPage, setRequestError]);

  useEffect(() => {
    let isActive = true;

    const loadAnchorPage = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await requestPage(undefined, anchor_period_id);

        if (!isActive) {
          return;
        }

        setPages(new Map());
        minimumPageRef.current = null;
        maximumPageRef.current = null;
        applyResponse(response);
      } catch (requestError) {
        if (isActive) {
          setRequestError(requestError);
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    void loadAnchorPage();

    return () => {
      isActive = false;
    };
  }, [anchor_period_id, applyResponse, requestPage, setRequestError]);

  return {
    periods,
    loading,
    loading_previous: loadingPrevious,
    loading_next: loadingNext,
    error,
    can_load_previous: canLoadPrevious,
    can_load_next: canLoadNext,
    anchor_period_id: resolvedAnchorPeriodId,
    load_previous: loadPrevious,
    load_next: loadNext,
    refresh_loaded_pages: refreshLoadedPages,
  };
};
