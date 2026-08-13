export type ScreenPropsOfType<
  TScreenMap,
  K extends keyof TScreenMap,
> = TScreenMap[K];
