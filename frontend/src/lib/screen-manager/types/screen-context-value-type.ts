import { type Dispatch, type RefObject, type SetStateAction } from 'react';

import { StackEntryType } from 'lib/screen-manager/types/stack-entry-type';

export interface ScreenContextValueType<TScreenMap> {
  stack: StackEntryType<TScreenMap>[];
  setStack: Dispatch<SetStateAction<StackEntryType<TScreenMap>[]>>;
  pendingFocusRef: RefObject<HTMLElement | null>;
  lastFocusedElementRef: RefObject<HTMLElement | null>;
  instanceKeyCounterRef: RefObject<number>;
}
