import ResolvedSidePeek from './resolved-side-peek';
import { SidePeekInvocation } from './side-peek-invocation';

export type SidePeekRegistryType<TSidePeekMap> = (
  ...invocation: SidePeekInvocation<TSidePeekMap>
) => ResolvedSidePeek<keyof TSidePeekMap & string>;
