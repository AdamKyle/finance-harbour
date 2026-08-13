import { match } from 'ts-pattern';

import { ButtonVariant } from 'ui/buttons/enums/button-variant';

type IconButtonVariantStylesType = {
  button: string;
  icon: string;
};

export const iconButtonVariantStyles = (
  variant: ButtonVariant
): IconButtonVariantStylesType => {
  return match(variant)
    .with(ButtonVariant.DANGER, () => ({
      button:
        'bg-persian-plum-600 text-white hover:bg-persian-plum-500 focus:ring-persian-plum-400 dark:focus:ring-persian-plum-600',
      icon: '',
    }))
    .with(ButtonVariant.SUCCESS, () => ({
      button:
        'bg-tom-thumb-600 text-white hover:bg-tom-thumb-500 focus:ring-tom-thumb-400 dark:focus:ring-tom-thumb-600',
      icon: '',
    }))
    .with(ButtonVariant.PRIMARY, () => ({
      button:
        'bg-blue-bell-600 text-white hover:bg-blue-bell-500 focus:ring-blue-bell-400 dark:focus:ring-blue-bell-600',
      icon: '',
    }))
    .with(ButtonVariant.Default, () => ({
      button:
        'border border-storm-dust-300 bg-white text-storm-dust-900 hover:bg-storm-dust-100 focus:ring-storm-dust-400 dark:border-storm-dust-700 dark:bg-storm-dust-900 dark:text-storm-dust-50 dark:hover:bg-storm-dust-800 dark:focus:ring-storm-dust-600',
      icon: '',
    }))
    .with(ButtonVariant.GHOST, () => ({
      button:
        'rounded-full bg-transparent text-storm-dust-800 shadow-none hover:bg-storm-dust-200 focus:bg-storm-dust-200 focus:ring-storm-dust-400 motion-safe:hover:scale-[1.07] motion-safe:focus:scale-[1.07] dark:text-storm-dust-100 dark:hover:bg-storm-dust-700 dark:focus:bg-storm-dust-700 dark:focus:ring-storm-dust-500',
      icon: '',
    }))
    .with(ButtonVariant.WARNING, () => ({
      button:
        'bg-sweet-corn-300 text-storm-dust-950 hover:bg-sweet-corn-200 focus:ring-sweet-corn-500 dark:bg-sweet-corn-700 dark:text-white dark:hover:bg-sweet-corn-600 dark:focus:ring-sweet-corn-400',
      icon: '',
    }))
    .otherwise(() => ({
      button: '',
      icon: '',
    }));
};
