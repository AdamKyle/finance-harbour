import { ScreenNameType } from './screen-name-type';
import { ScreenRenderArgsType } from './screen-render-args-type';

export type ScreenInvocationType<TScreenMap> = {
  [K in keyof TScreenMap]: [
    screen: K & ScreenNameType<TScreenMap>,
    ...args: ScreenRenderArgsType<TScreenMap, K>,
  ];
}[keyof TScreenMap];
