import UpdateBudgetValueRequestDefinition from './update-budget-value-request-definition';

export default interface UseUpdateBudgetValueDefinition {
  requestData: UpdateBudgetValueRequestDefinition;
  getRequestData: () => UpdateBudgetValueRequestDefinition;
  setRequestData: (requestData: UpdateBudgetValueRequestDefinition) => void;
  loading: boolean;
  error: string | null;
  updateValue: () => Promise<boolean>;
}
