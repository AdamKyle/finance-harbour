import { SaveLeftOverWarningThresholdRequestDefinition } from './save-left-over-warning-threshold-request-definition';

export interface UseSaveLeftOverWarningThresholdDefinition {
  save: (
    request: SaveLeftOverWarningThresholdRequestDefinition
  ) => Promise<{ ok: boolean; error?: string }>;
  loading: boolean;
}
