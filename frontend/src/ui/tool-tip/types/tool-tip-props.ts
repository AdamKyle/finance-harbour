import { ReactNode } from 'react';

export default interface ToolTipProps {
  id: string;
  label: string;
  children: ReactNode;
  additional_css?: string;
}
