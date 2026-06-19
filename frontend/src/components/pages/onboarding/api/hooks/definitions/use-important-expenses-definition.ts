import { ImportantExpenseCardDefinition } from './important-expense-card-definition';

import PaginatedApiHandlerDefinition from 'lib/api-handler/definitions/paginated-api-handler-definition';

export type UseImportantExpensesDefinition = PaginatedApiHandlerDefinition<
  ImportantExpenseCardDefinition,
  Record<string, unknown>
>;
