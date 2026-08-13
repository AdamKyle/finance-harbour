import { resolveFHScreen } from './screen-manager-registry';

import { createScreenManager } from 'lib/screen-manager/create-screen-manager';

export const {
  ScreenManagerProvider: FHScreenManagerProvider,
  ScreenHost: FHScreenHost,
  ScreenBindingHost: FHScreenBindingHost,
  useScreenNavigation: useFHScreenNavigation,
  useBindScreen: useFHBindScreen,
} = createScreenManager(resolveFHScreen);
