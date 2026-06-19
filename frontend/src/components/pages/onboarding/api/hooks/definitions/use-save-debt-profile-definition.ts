import { SaveDebtProfileRequestDefinition } from './save-debt-profile-request-definition';

export interface UseSaveDebtProfileDefinition {
  save: (
    data: SaveDebtProfileRequestDefinition
  ) => Promise<{ ok: boolean; error?: string }>;
  loading: boolean;
}
