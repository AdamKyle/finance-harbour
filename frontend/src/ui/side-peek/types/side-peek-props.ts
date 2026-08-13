import { ReactNode, Ref } from 'react';

export default interface SidePeekProps {
  title: string;
  children: ReactNode;
  on_close: () => void;
  panel_ref: Ref<HTMLDivElement>;
}
