import ScreenTransitionConfig from 'lib/screen-manager/types/screen-transition-config';

const screenTransition: ScreenTransitionConfig = {
  duration: 0.45,
  ease: 'easeOut',
};

export const normalMotionProps = {
  initial: { x: '100%', opacity: 0 },
  animate: { x: 0, opacity: 1 },
  exit: { x: '100%', opacity: 0 },
  transition: screenTransition,
};

export const reducedMotionProps = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0 },
};
