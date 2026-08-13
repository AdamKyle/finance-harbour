export default interface AddBudgetBillRequestDefinition {
  title: string;
  amount_dollars: string;
  is_required: boolean;
  going_forward: boolean;
}
