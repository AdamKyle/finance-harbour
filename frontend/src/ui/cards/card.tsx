import clsx from 'clsx';
import type { ReactNode } from 'react';

import type CardProps from './types/card-props';

const Card = ({
  children,
  additional_css,
  content_css,
}: CardProps): ReactNode => {
  return (
    <div
      className={clsx(
        'border-storm-dust-200 rounded-sm border bg-white shadow-sm',
        'dark:border-storm-dust-700 dark:bg-storm-dust-800 dark:text-storm-dust-100',
        additional_css
      )}
    >
      <div className={clsx('p-3 md:p-4 xl:p-6', content_css)}>{children}</div>
    </div>
  );
};

export default Card;
