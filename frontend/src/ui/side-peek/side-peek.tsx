import { useId } from 'react';

import SidePeekProps from './types/side-peek-props';

import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';

const SidePeek = ({ title, children, on_close, panel_ref }: SidePeekProps) => {
  const titleId = useId();

  return (
    <section
      ref={panel_ref}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      tabIndex={-1}
      className="border-storm-dust-200 dark:border-storm-dust-700 dark:bg-storm-dust-900 flex h-dvh w-full flex-col border-l bg-white shadow-2xl outline-none sm:w-[32rem] sm:max-w-[90vw]"
    >
      <header className="border-storm-dust-200 dark:border-storm-dust-700 flex items-center justify-between gap-4 border-b px-4 py-3 pt-[max(0.75rem,env(safe-area-inset-top))]">
        <h2 id={titleId} className="text-lg font-bold">
          {title}
        </h2>
        <IconButton
          icon="fa-solid fa-xmark"
          label="Close side peek"
          aria_label="Close side peek"
          variant={ButtonVariant.GHOST}
          on_click={on_close}
        />
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-2 pb-[max(1rem,env(safe-area-inset-bottom))]">
        {children}
      </div>
    </section>
  );
};

export default SidePeek;
