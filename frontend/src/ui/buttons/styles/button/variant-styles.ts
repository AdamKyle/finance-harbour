import { match } from 'ts-pattern';

import { ButtonVariant } from 'ui/buttons/enums/button-variant';

export const variantStyles = (variant: ButtonVariant): string => {
  return match(variant)
    .with(
      ButtonVariant.DANGER,
      () =>
        'bg-persian-plum-600 text-white hover:bg-persian-plum-500 focus:ring-persian-plum-400 dark:focus:ring-persian-plum-600'
    )
    .with(
      ButtonVariant.SUCCESS,
      () =>
        'bg-tom-thumb-600 text-white hover:bg-tom-thumb-500 focus:ring-tom-thumb-400 dark:focus:ring-tom-thumb-600'
    )
    .with(
      ButtonVariant.PRIMARY,
      () =>
        'bg-blue-bell-600 text-white hover:bg-blue-bell-500 focus:ring-blue-bell-400 dark:focus:ring-blue-bell-600'
    )
    .with(
      ButtonVariant.Default,
      () =>
        'border border-storm-dust-300 bg-white text-storm-dust-900 hover:bg-storm-dust-100 focus:ring-storm-dust-400 dark:border-storm-dust-700 dark:bg-storm-dust-900 dark:text-storm-dust-50 dark:hover:bg-storm-dust-800 dark:focus:ring-storm-dust-600'
    )
    .with(
      ButtonVariant.WARNING,
      () =>
        'bg-sweet-corn-300 text-storm-dust-950 hover:bg-sweet-corn-200 focus:ring-sweet-corn-500 dark:bg-sweet-corn-700 dark:text-white dark:hover:bg-sweet-corn-600 dark:focus:ring-sweet-corn-400'
    )
    .with(
      ButtonVariant.GHOST,
      () =>
        'bg-transparent text-storm-dust-800 hover:bg-storm-dust-200 focus:ring-storm-dust-400 dark:text-storm-dust-100 dark:hover:bg-storm-dust-700 dark:focus:ring-storm-dust-500'
    )
    .otherwise(() => '');
};
