import { useState } from 'react';

import DarkModeProviderProps from './types/dark-mode-provider-props';

import { THEME_STORAGE_KEY } from 'ui/dark-mode-toggle/constants/theme-storage-key';
import { DarkModeContext } from 'ui/dark-mode-toggle/context/dark-mode-context';

export const DarkModeProvider = ({ children }: DarkModeProviderProps) => {
  const [isDarkMode, setIsDarkMode] = useState(
    () => globalThis.localStorage.getItem(THEME_STORAGE_KEY) === 'dark'
  );

  const toggleDarkMode = () => {
    setIsDarkMode((currentValue) => {
      const nextValue = !currentValue;
      let nextStoredValue = 'light';

      if (nextValue) {
        nextStoredValue = 'dark';
      }

      globalThis.localStorage.setItem(THEME_STORAGE_KEY, nextStoredValue);

      return nextValue;
    });
  };

  const getRootClassName = () => {
    if (isDarkMode) {
      return 'dark min-h-screen';
    }

    return 'min-h-screen';
  };
  const rootClassName = getRootClassName();

  return (
    <DarkModeContext.Provider
      value={{
        is_dark_mode: isDarkMode,
        toggle_dark_mode: toggleDarkMode,
      }}
    >
      <div className={rootClassName}>{children}</div>
    </DarkModeContext.Provider>
  );
};
