import { useEffect, useRef } from 'react';

import UseMountedRefDefinition from './definitions/use-mounted-ref-definition';

export const useMountedRef = (): UseMountedRefDefinition => {
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return isMountedRef;
};
