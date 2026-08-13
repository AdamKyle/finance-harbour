import { ScreenInvocationType } from './screen-invocation-type';

export interface NavigationType<TScreenMap> {
  navigateTo: (...invocation: ScreenInvocationType<TScreenMap>) => void;
  replaceWith: (...invocation: ScreenInvocationType<TScreenMap>) => void;
  resetTo: (...invocation: ScreenInvocationType<TScreenMap>) => void;
  pop: (count?: number) => void;
  stackDepth: number;
}
