export default interface BudgetPeriodsRecalculatedEventPayload {
  source_pay_period_id: number;
  affected_pay_period_ids: number[];
}
