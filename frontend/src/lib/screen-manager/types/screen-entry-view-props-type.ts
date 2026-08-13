import { StackEntryType } from 'lib/screen-manager/types/stack-entry-type';

export interface ScreenEntryViewPropsType<TScreenMap> {
  entry: StackEntryType<TScreenMap>;
  isActive: boolean;
  setRef: (element: HTMLDivElement | null) => void;
}
