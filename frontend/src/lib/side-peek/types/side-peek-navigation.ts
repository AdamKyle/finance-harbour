import { SidePeekInvocation } from './side-peek-invocation';

export default interface SidePeekNavigation<TSidePeekMap> {
  push: (...invocation: SidePeekInvocation<TSidePeekMap>) => void;
  replace: (...invocation: SidePeekInvocation<TSidePeekMap>) => void;
  pop: () => void;
  closeAll: () => void;
  stackDepth: number;
}
