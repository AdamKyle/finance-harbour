import { motion, useReducedMotion } from 'motion/react';
import { KeyboardEvent, ReactNode, useEffect, useId, useRef } from 'react';
import { useNavigate } from 'react-router';

import SlidingContentPanelProps from './types/sliding-content-panel-props';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { navigateToRoute } from 'router/utils/navigate-to-route';

import Card from 'ui/cards/card';

const SlidingContentPanel = ({
  children,
  title,
}: SlidingContentPanelProps): ReactNode => {
  const navigate = useNavigate();
  const titleId = useId();
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    closeButtonRef.current?.focus();
  }, []);

  const handleClose = () => {
    navigateToRoute(navigate, NavigationRoutes.HOME);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key !== 'Escape') {
      return;
    }

    event.preventDefault();
    handleClose();
  };

  const getInitialAnimation = () => {
    if (shouldReduceMotion) {
      return false;
    }

    return { x: '100%', opacity: 0 };
  };

  const getTransition = () => {
    if (shouldReduceMotion) {
      return { duration: 0 };
    }

    return { duration: 0.28 };
  };

  return (
    <motion.main
      role="dialog"
      aria-modal="false"
      aria-labelledby={titleId}
      onKeyDown={handleKeyDown}
      initial={getInitialAnimation()}
      animate={{ x: 0, opacity: 1 }}
      transition={getTransition()}
      className="bg-storm-dust-50 text-storm-dust-950 dark:bg-storm-dust-950 dark:text-storm-dust-50 flex min-h-0 flex-1 overflow-y-auto px-4 py-8 transition-colors sm:px-6 sm:py-12 lg:py-16"
    >
      <section aria-labelledby={titleId} className="mx-auto w-full max-w-6xl">
        <div className="mb-6 flex items-center gap-3 sm:mb-8">
          <button
            ref={closeButtonRef}
            type="button"
            onClick={handleClose}
            aria-label={`Close ${title}`}
            className="focus:ring-storm-dust-400 text-storm-dust-700 hover:border-storm-dust-300 hover:bg-storm-dust-100 dark:text-storm-dust-200 dark:hover:border-storm-dust-600 dark:hover:bg-storm-dust-800 inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-transparent transition focus:ring-2 focus:outline-hidden"
          >
            <i className="fa-solid fa-xmark" aria-hidden="true" />
          </button>

          <h1
            id={titleId}
            className="text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl"
          >
            {title}
          </h1>
        </div>

        <Card>{children}</Card>
      </section>
    </motion.main>
  );
};

export default SlidingContentPanel;
