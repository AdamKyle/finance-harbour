import { FinanceHarbourSidePeek } from './enums/finance-harbour-side-peek';
import { FHSidePeekMap } from './side-peek-props';

import { SidePeekRegistryType } from 'lib/side-peek/types/side-peek-registry-type';

import AddBillSidePeek from 'components/side-peeks/add-bill/add-bill-side-peek';

export const resolveFHSidePeek: SidePeekRegistryType<FHSidePeekMap> = (
  ...invocation
) => {
  const sidePeek = invocation[0];

  switch (sidePeek) {
    case FinanceHarbourSidePeek.ADD_BILL:
      return {
        name: FinanceHarbourSidePeek.ADD_BILL,
        title: 'Add a recurring payment',
        dismissible: true,
        render_content: () => <AddBillSidePeek />,
      };
  }
};
