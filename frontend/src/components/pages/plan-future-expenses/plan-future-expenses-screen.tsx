import { NavigationRoutes } from 'router/enums/navigation-routes';

import SectionWithTitle from 'ui/sections/section-with-title';

const PlanFutureExpensesScreen = () => {
  return (
    <SectionWithTitle
      title="Plan future expenses"
      back_route={NavigationRoutes.DASHBOARD}
    />
  );
};

export default PlanFutureExpensesScreen;
