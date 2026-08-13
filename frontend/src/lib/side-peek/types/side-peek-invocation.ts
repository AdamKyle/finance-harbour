export type SidePeekInvocation<TSidePeekMap> = {
  [K in keyof TSidePeekMap]: [
    name: K & string,
    props: TSidePeekMap[K],
    opener: HTMLElement | null,
  ];
}[keyof TSidePeekMap];
