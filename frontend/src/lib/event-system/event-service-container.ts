import EventSystemDefinition from './definitions/event-system-definition';
import EventSystem from './event-system';

import { ModularContainerDefinition } from 'configuration/deffinitions/modular-container-definition';

import CoreContainerDefinition from 'lib/service-container/deffinitions/core-container-definition';

export const eventServiceContainer: ModularContainerDefinition = (
  container: CoreContainerDefinition
) => {
  container.register<EventSystemDefinition>('EventSystem', new EventSystem());
};
