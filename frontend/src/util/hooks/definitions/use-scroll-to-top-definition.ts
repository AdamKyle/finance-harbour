import { RefObject } from 'react';

export interface UseScrollToTopOptions {
  targetRef?: RefObject<HTMLElement | null>;
  focusTarget?: boolean;
}

export default interface UseScrollToTopDefinition {
  scrollToTop: () => void;
}
