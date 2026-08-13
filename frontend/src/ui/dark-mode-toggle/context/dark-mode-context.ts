import { createContext } from 'react';

export interface DarkModeContextDefinition {
  is_dark_mode: boolean;
  toggle_dark_mode: () => void;
}

export const DarkModeContext = createContext<DarkModeContextDefinition | null>(
  null
);
