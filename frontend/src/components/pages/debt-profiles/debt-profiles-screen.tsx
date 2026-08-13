import { NavigationRoutes } from 'router/enums/navigation-routes';

import SectionWithTitle from 'ui/sections/section-with-title';

const DebtProfilesScreen = () => {
  return (
    <SectionWithTitle
      title="Debt profiles"
      back_route={NavigationRoutes.DASHBOARD}
    />
  );
};

export default DebtProfilesScreen;
