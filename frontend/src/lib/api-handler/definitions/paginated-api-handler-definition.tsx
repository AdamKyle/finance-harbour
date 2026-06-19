import { PaginatedApiResponseDefinition } from 'lib/api-handler/definitions/paginated-api-response-definition';
import { StateSetter } from 'lib/types/state-setter-type';

export default interface PaginatedApiHandlerDefinition<
  T,
  F extends Record<string, unknown>,
> {
  data: T[];
  response: PaginatedApiResponseDefinition<T[]> | null;
  error: unknown | null;
  loading: boolean;
  canLoadMore: boolean;
  isLoadingMore: boolean;
  page: number;
  setPage: StateSetter<number>;
  setSearchText: StateSetter<string>;
  setFilters: StateSetter<F>;
  onEndReached: () => void;
  setRefresh: StateSetter<boolean>;
}
