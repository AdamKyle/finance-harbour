import clsx from 'clsx';

import type ToolTipProps from './types/tool-tip-props';

const ToolTip = ({ id, label, children, additional_css }: ToolTipProps) => {
  return (
    <div className={clsx('group relative inline-flex', additional_css)}>
      {children}
      <div
        id={id}
        role="tooltip"
        className="bg-storm-dust-800 text-storm-dust-50 dark:bg-storm-dust-900 dark:ring-storm-dust-700 pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 w-max max-w-[min(14rem,calc(100vw-2rem))] -translate-x-1/2 rounded px-2 py-1 text-center text-xs leading-snug wrap-break-word opacity-0 transition-opacity duration-150 group-focus-within:opacity-100 group-hover:opacity-100 motion-reduce:transition-none dark:ring-1"
      >
        {label}
      </div>
    </div>
  );
};

export default ToolTip;
