export default interface UsePaydayBacklogProgressionDefinition {
  is_caught_up: boolean;
  finish_payday: () => Promise<boolean>;
}
