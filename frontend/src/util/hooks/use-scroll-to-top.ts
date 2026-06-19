import { useCallback, useEffect, useRef } from 'react';

import UseScrollToTopDefinition, {
  UseScrollToTopOptions,
} from './definitions/use-scroll-to-top-definition';

export const useScrollToTop = ({
  targetRef,
  focusTarget = false,
}: UseScrollToTopOptions = {}): UseScrollToTopDefinition => {
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current === null) {
        return;
      }

      window.cancelAnimationFrame(animationFrameRef.current);
    };
  }, []);

  const scrollToTop = useCallback(() => {
    if (animationFrameRef.current !== null) {
      window.cancelAnimationFrame(animationFrameRef.current);
    }

    animationFrameRef.current = window.requestAnimationFrame(() => {
      animationFrameRef.current = null;

      const targetElement = targetRef?.current;

      if (!targetElement) {
        window.scrollTo({
          behavior: 'smooth',
          top: 0,
        });

        return;
      }

      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });

      if (!focusTarget) {
        return;
      }

      targetElement.focus({ preventScroll: true });
    });
  }, [focusTarget, targetRef]);

  return {
    scrollToTop,
  };
};
