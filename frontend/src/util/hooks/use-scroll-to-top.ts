import { useCallback } from 'react';

import UseScrollToTopDefinition, {
  UseScrollToTopOptions,
} from './definitions/use-scroll-to-top-definition';

export const useScrollToTop = ({
  targetRef,
  focusTarget = false,
}: UseScrollToTopOptions = {}): UseScrollToTopDefinition => {
  const scrollToTop = useCallback(() => {
    const targetElement = targetRef?.current;

    if (targetElement === undefined || targetElement === null) {
      return;
    }

    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });

    if (focusTarget) {
      targetElement.focus({ preventScroll: true });
    }
  }, [focusTarget, targetRef]);

  return { scrollToTop };
};
