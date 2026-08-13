import { useContext } from 'react';

import { DarkModeContext } from 'ui/dark-mode-toggle/context/dark-mode-context';
import UseDarkModeDefinition from 'ui/dark-mode-toggle/hooks/definitions/use-dark-mode-definition';

export const useDarkMode = (): UseDarkModeDefinition => {
  const context = useContext(DarkModeContext);

  if (context === null) {
    throw new Error('useDarkMode must be used within DarkModeProvider');
  }

  let darkModeLabel = 'Dark mode';
  let darkModeAriaLabel = 'Switch to dark mode';
  let darkModeIconClassName = 'fa-solid fa-moon';

  if (context.is_dark_mode) {
    darkModeLabel = 'Light mode';
    darkModeAriaLabel = 'Switch to light mode';
    darkModeIconClassName = 'fa-solid fa-sun';
  }

  return {
    darkModeAriaLabel,
    darkModeIconClassName,
    darkModeLabel,
    isDarkMode: context.is_dark_mode,
    onToggleDarkMode: context.toggle_dark_mode,
  };
};

export default useDarkMode;
