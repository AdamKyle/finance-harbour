import { type ReactNode } from 'react';

import { ScreenInvocationType } from './screen-invocation-type';
import { ScreenNameType } from './screen-name-type';

export interface ResolvedScreenType<TScreenMap> {
  screenName: ScreenNameType<TScreenMap>;
  dismissible: boolean;
  renderContent: () => ReactNode;
}

export type RegistryType<TScreenMap> = (
  ...invocation: ScreenInvocationType<TScreenMap>
) => ResolvedScreenType<TScreenMap>;
