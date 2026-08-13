import { resolveFHSidePeek } from './side-peek-registry';

import { createSidePeekManager } from 'lib/side-peek/create-side-peek-manager';

export const {
  SidePeekProvider: FHSidePeekProvider,
  SidePeekHost: FHSidePeekHost,
  useSidePeekNavigation: useFHSidePeekNavigation,
} = createSidePeekManager(resolveFHSidePeek);
