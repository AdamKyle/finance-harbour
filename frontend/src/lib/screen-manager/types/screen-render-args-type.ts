import { ScreenPropsOfType } from './screen-props-of-type';

export type ScreenRenderArgsType<TScreenMap, K extends keyof TScreenMap> =
  ScreenPropsOfType<TScreenMap, K> extends undefined
    ? []
    : [props: ScreenPropsOfType<TScreenMap, K>];
