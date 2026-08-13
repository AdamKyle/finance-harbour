import { ModularContainerDefinition } from './deffinitions/modular-container-definition';

import { axiosServiceContainer } from 'lib/api-handler/axios-service-container';
import { eventServiceContainer } from 'lib/event-system/event-service-container';

/**
 * Register service containers here.
 */
export const serviceContainers: ModularContainerDefinition[] = [
  eventServiceContainer,
  axiosServiceContainer,
];
