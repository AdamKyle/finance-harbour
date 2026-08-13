import AddBudgetBillRequestDefinition from './add-budget-bill-request-definition';

export default interface UseAddBudgetBillDefinition {
  requestData: AddBudgetBillRequestDefinition;
  setRequestData: (requestData: AddBudgetBillRequestDefinition) => void;
  loading: boolean;
  error: string | null;
  addBill: () => Promise<boolean>;
}
