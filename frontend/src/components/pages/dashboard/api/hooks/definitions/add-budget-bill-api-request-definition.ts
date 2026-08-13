export default interface AddBudgetBillApiRequestDefinition {
  title: string;
  amount_cents: number;
  is_required: boolean;
  going_forward: boolean;
}
