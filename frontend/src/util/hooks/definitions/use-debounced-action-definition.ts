export default interface UseDebouncedActionDefinition {
  flush: () => void;
  schedule: () => void;
}
