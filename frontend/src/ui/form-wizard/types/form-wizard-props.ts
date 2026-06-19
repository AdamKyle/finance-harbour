import { ReactNode } from 'react';

import { AxiosErrorDefinition } from 'lib/api-handler/definitions/axios-error-definition';

export default interface FormWizardProps {
  total_steps: number;
  initial_index?: number;
  name?: string;
  is_loading?: boolean;
  render_loading_icon?: () => ReactNode;
  on_request_next?: (current_index: number) => Promise<boolean> | boolean;
  children: ReactNode;
  form_error: AxiosErrorDefinition | null;
}
