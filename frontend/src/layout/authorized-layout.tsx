import { type ReactNode } from 'react';

import { FHScreenManagerProvider } from 'configuration/screen-manager/screen-manager-kit';

import BaseAuthenticatedNavigation from 'components/authenticated-navigation/base-authenticated-navigation';
import PaydayQueueProvider from 'components/pages/payday/context/payday-queue-provider';
import PaydayAutoNavigator from 'components/pages/payday/payday-auto-navigator';

import AuthorizedLayoutContent from 'layout/components/authorized-layout-content';

const AuthorizedLayout = (): ReactNode => {
  return (
    <FHScreenManagerProvider>
      <PaydayQueueProvider>
        <div className="bg-storm-dust-50 text-storm-dust-950 dark:bg-storm-dust-950 dark:text-storm-dust-50 flex min-h-dvh flex-col transition-colors duration-200">
          <BaseAuthenticatedNavigation />
          <PaydayAutoNavigator />

          <AuthorizedLayoutContent />
        </div>
      </PaydayQueueProvider>
    </FHScreenManagerProvider>
  );
};

export default AuthorizedLayout;
