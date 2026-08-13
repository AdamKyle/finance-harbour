import clsx from 'clsx';

import type { IndeterminateProgressBarProps } from './types/indeterminate-progress-bar-props';

const IndeterminateProgressBar = ({
  label,
  additional_css,
}: IndeterminateProgressBarProps) => {
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuetext="Loading"
      className={clsx(
        'bg-storm-dust-200 dark:bg-storm-dust-700 h-2 w-full overflow-hidden rounded-full',
        additional_css
      )}
    >
      <div
        aria-hidden="true"
        className="animate-indeterminate bg-blue-bell-500 h-full w-1/3 rounded-full motion-reduce:w-full motion-reduce:animate-none"
      />
    </div>
  );
};

export default IndeterminateProgressBar;
