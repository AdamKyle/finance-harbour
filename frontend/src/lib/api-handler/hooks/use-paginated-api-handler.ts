import { AxiosError, AxiosRequestConfig } from 'axios';
import { useCallback, useEffect, useRef, useState } from 'react';

import ApiParametersDefinitions from 'lib/api-handler/definitions/api-parameters-definitions';
import PaginatedApiHandlerDefinition from 'lib/api-handler/definitions/paginated-api-handler-definition';
import { PaginatedApiResponseDefinition } from 'lib/api-handler/definitions/paginated-api-response-definition';
import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { shallowEqual } from 'lib/api-handler/utils/shallow-equal';

const UsePaginatedApiHandler = <
  T,
  F extends Record<string, unknown> = Record<string, unknown>,
>(
  params: ApiParametersDefinitions,
  perPage: number,
  initialFilters: F
): PaginatedApiHandlerDefinition<T, F> => {
  const { apiHandler, getUrl } = useApiHandler();
  const url = getUrl(params.url, params.urlParams);

  const [data, setData] = useState<T[]>([]);
  const [response, setResponse] = useState<PaginatedApiResponseDefinition<
    T[]
  > | null>(null);
  const [error, setError] =
    useState<PaginatedApiHandlerDefinition<T, F>['error']>(null);
  const [loading, setLoading] = useState(true);
  const [canLoadMore, setCanLoadMore] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState<F>(initialFilters);
  const [refresh, setRefresh] = useState(false);

  const previousSearchTextRef = useRef(searchText);
  const previousFiltersRef = useRef<F>(filters);
  const previousAdditionalParamsRef = useRef(params.additionalParams);
  const pageAdvanceLockRef = useRef(false);
  const requestSequenceRef = useRef(0);

  const handleRequestError = useCallback(
    (errorInstance: unknown) => {
      if (errorInstance instanceof AxiosError) {
        const axiosResponse = errorInstance.response;

        if (!axiosResponse) {
          setError({ message: errorInstance.message });

          return;
        }

        setError(axiosResponse.data || { message: errorInstance.message });

        return;
      }

      setError({
        message:
          'We could not load the requested information. Please try again.',
      });
    },
    [setError]
  );

  const fetchPaginatedData = useCallback(async () => {
    if (params.enabled === false) {
      setLoading(false);

      return;
    }

    requestSequenceRef.current += 1;
    const requestSequence = requestSequenceRef.current;
    setError(null);

    if (page === 1) {
      setLoading(true);
    } else {
      setIsLoadingMore(true);
    }

    try {
      const result = await apiHandler.get<
        PaginatedApiResponseDefinition<T[]>,
        AxiosRequestConfig<PaginatedApiResponseDefinition<T[]>>
      >(url, {
        params: {
          per_page: perPage,
          page,
          search_text: searchText,
          filters,
          ...params.additionalParams,
        },
      });

      if (requestSequence !== requestSequenceRef.current) {
        return;
      }

      setResponse(result);
      setData((previousData) =>
        page === 1 ? result.data : [...previousData, ...result.data]
      );
      setCanLoadMore(result.meta.can_load_more);
    } catch (errorInstance) {
      if (requestSequence === requestSequenceRef.current) {
        handleRequestError(errorInstance);
      }
    } finally {
      if (requestSequence === requestSequenceRef.current) {
        setLoading(false);
        setIsLoadingMore(false);
        pageAdvanceLockRef.current = false;
      }
    }
  }, [
    apiHandler,
    filters,
    handleRequestError,
    page,
    params.additionalParams,
    params.enabled,
    perPage,
    searchText,
    url,
  ]);

  const reloadLoadedPages = useCallback(async () => {
    if (params.enabled === false) {
      return;
    }

    requestSequenceRef.current += 1;
    const requestSequence = requestSequenceRef.current;
    const highestLoadedPage = page;
    setError(null);
    setLoading(true);

    try {
      const pageRequests = Array.from(
        { length: highestLoadedPage },
        (_, pageIndex) =>
          apiHandler.get<
            PaginatedApiResponseDefinition<T[]>,
            AxiosRequestConfig<PaginatedApiResponseDefinition<T[]>>
          >(url, {
            params: {
              per_page: perPage,
              page: pageIndex + 1,
              search_text: searchText,
              filters,
              ...params.additionalParams,
            },
          })
      );
      const pageResponses = await Promise.all(pageRequests);

      if (requestSequence !== requestSequenceRef.current) {
        return;
      }

      const latestResponse = pageResponses[pageResponses.length - 1];
      setData(pageResponses.flatMap((pageResponse) => pageResponse.data));
      setResponse(latestResponse);
      setCanLoadMore(latestResponse.meta.can_load_more);
    } catch (errorInstance) {
      if (requestSequence === requestSequenceRef.current) {
        handleRequestError(errorInstance);
      }
    } finally {
      if (requestSequence === requestSequenceRef.current) {
        setLoading(false);
        setIsLoadingMore(false);
        pageAdvanceLockRef.current = false;
      }
    }
  }, [
    apiHandler,
    filters,
    handleRequestError,
    page,
    params.additionalParams,
    params.enabled,
    perPage,
    searchText,
    url,
  ]);

  useEffect(() => {
    void fetchPaginatedData();
  }, [fetchPaginatedData, refresh]);

  useEffect(() => {
    const isSameSearch = previousSearchTextRef.current === searchText;

    const isSameFilters = shallowEqual(previousFiltersRef.current, filters);
    const isSameAdditionalParams = shallowEqual(
      previousAdditionalParamsRef.current ?? {},
      params.additionalParams ?? {}
    );

    if (isSameSearch && isSameFilters && isSameAdditionalParams) {
      return;
    }

    previousSearchTextRef.current = searchText;

    previousFiltersRef.current = filters;
    previousAdditionalParamsRef.current = params.additionalParams;

    setData([]);
    setResponse(null);
    setPage(1);
    setRefresh((previousValue) => !previousValue);
  }, [filters, params.additionalParams, searchText]);

  const onEndReached = () => {
    if (!canLoadMore) {
      return;
    }

    if (isLoadingMore) {
      return;
    }

    if (pageAdvanceLockRef.current) {
      return;
    }

    pageAdvanceLockRef.current = true;
    setPage((previousValue) => previousValue + 1);
  };

  return {
    data,
    response,
    error,
    loading,
    canLoadMore,
    isLoadingMore,
    page,
    onEndReached,
    reloadLoadedPages,
    setSearchText,
    setFilters,
    setPage,
    setRefresh,
  };
};

export default UsePaginatedApiHandler;
