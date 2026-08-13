import { type ReactNode } from 'react';

import { FHScreenManagerProvider } from 'configuration/screen-manager/screen-manager-kit';
import { FHSidePeekProvider } from 'configuration/side-peek/side-peek-kit';

import PaydayQueueProvider from 'components/pages/payday/context/payday-queue-provider';

import AuthorizedLayoutContent from 'layout/components/authorized-layout-content';

const AuthorizedLayout = (): ReactNode => {
  return (
    <FHScreenManagerProvider>
      <FHSidePeekProvider>
        <PaydayQueueProvider>
          <AuthorizedLayoutContent />
        </PaydayQueueProvider>
      </FHSidePeekProvider>
    </FHScreenManagerProvider>
  );
};

export default AuthorizedLayout;
