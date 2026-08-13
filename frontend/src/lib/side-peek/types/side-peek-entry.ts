import { ReactNode } from 'react';

export default interface SidePeekEntry<Name extends string> {
  instance_key: string;
  name: Name;
  title: string;
  render_content: () => ReactNode;
  dismissible: boolean;
  opener: HTMLElement | null;
}
