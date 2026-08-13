import { ReactNode } from 'react';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';

export default interface FormWizardProps {
  total_steps: number;
  initial_index?: number;
  requested_index?: number;
  name?: string;
  is_loading?: boolean;
  render_loading_icon?: () => ReactNode;
  on_request_next?: (current_index: number) => Promise<boolean> | boolean;
  on_request_step_change?: (
    current_index: number,
    target_index: number
  ) => Promise<boolean> | boolean;
  children: ReactNode;
  form_error: AxiosErrorDefinition | null;
  available_step_indexes: number[];
  render_card?: boolean;
}
