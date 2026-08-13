import { ReactNode } from 'react';

export default interface ResolvedSidePeek<Name extends string> {
  name: Name;
  title: string;
  dismissible: boolean;
  render_content: () => ReactNode;
}
