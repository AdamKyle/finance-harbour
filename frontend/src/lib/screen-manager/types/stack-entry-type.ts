import { type ReactNode } from 'react';

import { ScreenNameType } from './screen-name-type';

export interface StackEntryType<TScreenMap> {
  instanceKey: string;
  screenName: ScreenNameType<TScreenMap>;
  renderContent: () => ReactNode;
  dismissible: boolean;
  bindingOwnerKey?: string;
  openedByElement: HTMLElement | null;
}
