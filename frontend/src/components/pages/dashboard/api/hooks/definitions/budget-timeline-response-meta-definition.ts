export default interface BudgetTimelineResponseMetaDefinition {
  can_load_previous: boolean;
  can_load_more: boolean;
  anchor_period_id: number | null;
  pagination: {
    current_page: number;
  };
}
