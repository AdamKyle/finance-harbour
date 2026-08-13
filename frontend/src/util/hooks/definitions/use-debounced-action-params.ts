export default interface UseDebouncedActionParams {
  action: () => void | Promise<void>;
  delay_ms: number;
}
