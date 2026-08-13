import type { ReactNode } from 'react';

export default interface CardProps {
  children: ReactNode;
  additional_css?: string;
  content_css?: string;
}
