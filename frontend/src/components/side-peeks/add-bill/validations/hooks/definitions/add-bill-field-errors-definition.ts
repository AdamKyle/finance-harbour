export default interface AddBillFieldErrorsDefinition {
  kind?: string;
  label?: string;
  amount_dollars?: string;
  current_balance_dollars?: string;
  minimum_payment_dollars?: string;
  current_payment_dollars?: string;
  payment_schedule?: string;
}
