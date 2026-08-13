import { ReactNode } from 'react';

import { NavigationRoutes } from 'router/enums/navigation-routes';

export default interface SectionWithTitleProps {
  children?: ReactNode;
  title: string;
  back_route?: NavigationRoutes;
  back_state?: object;
  on_back?: () => void;
}
