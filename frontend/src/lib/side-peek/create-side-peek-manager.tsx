import clsx from 'clsx';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import {
  createContext,
  KeyboardEvent,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { SidePeekEvent } from './events/side-peek-event';
import { SidePeekEventEmitterName } from './events/side-peek-event-emitter-name';
import SidePeekEntry from './types/side-peek-entry';
import { SidePeekInvocation } from './types/side-peek-invocation';
import SidePeekNavigation from './types/side-peek-navigation';
import SidePeekProviderProps from './types/side-peek-provider-props';
import { SidePeekRegistryType } from './types/side-peek-registry-type';

import { useEventSystem } from 'lib/event-system/hooks/use-event-system';

import SidePeek from 'ui/side-peek/side-peek';

const createSidePeekManager = <TSidePeekMap,>(
  resolve: SidePeekRegistryType<TSidePeekMap>
) => {
  type Name = keyof TSidePeekMap & string;
  interface OpenPayload {
    entry: SidePeekEntry<Name>;
  }

  interface EmptyPayload {
    requested: true;
  }

  interface SidePeekEventMap {
    [SidePeekEvent.PUSH]: OpenPayload;
    [SidePeekEvent.REPLACE]: OpenPayload;
    [SidePeekEvent.POP]: EmptyPayload;
    [SidePeekEvent.CLOSE_ALL]: EmptyPayload;
  }

  interface ContextValue {
    stack: SidePeekEntry<Name>[];
    restore_focus: (opener: HTMLElement | null) => void;
  }

  const Context = createContext<ContextValue | null>(null);
  let instanceSequence = 0;

  const useSidePeekContext = () => {
    const context = useContext(Context);

    if (context === null) {
      throw new Error(
        'Side Peek hooks must be used within the Side Peek provider.'
      );
    }

    return context;
  };

  const SidePeekProvider = ({ children }: SidePeekProviderProps) => {
    const eventSystem = useEventSystem();
    const [stack, setStack] = useState<SidePeekEntry<Name>[]>([]);
    const pendingFocusRef = useRef<HTMLElement | null>(null);

    useEffect(() => {
      const emitter = eventSystem.fetchOrCreateEventEmitter<SidePeekEventMap>(
        SidePeekEventEmitterName.SIDE_PEEK
      );
      const handlePush = ({ entry }: OpenPayload) =>
        setStack((current) => [...current, entry]);
      const handleReplace = ({ entry }: OpenPayload) =>
        setStack((current) =>
          current.length === 0 ? [entry] : [...current.slice(0, -1), entry]
        );
      const handlePop = (_payload: EmptyPayload) => {
        setStack((current) => {
          const top = current[current.length - 1];

          if (top === undefined || !top.dismissible) {
            return current;
          }

          pendingFocusRef.current = top.opener;

          return current.slice(0, -1);
        });
      };
      const handleCloseAll = (_payload: EmptyPayload) => {
        setStack((current) => {
          if (current.length > 0) {
            pendingFocusRef.current = current[0].opener;
          }

          return [];
        });
      };

      emitter.on(SidePeekEvent.PUSH, handlePush);
      emitter.on(SidePeekEvent.REPLACE, handleReplace);
      emitter.on(SidePeekEvent.POP, handlePop);
      emitter.on(SidePeekEvent.CLOSE_ALL, handleCloseAll);

      return () => {
        emitter.off(SidePeekEvent.PUSH, handlePush);
        emitter.off(SidePeekEvent.REPLACE, handleReplace);
        emitter.off(SidePeekEvent.POP, handlePop);
        emitter.off(SidePeekEvent.CLOSE_ALL, handleCloseAll);
      };
    }, [eventSystem]);

    useEffect(() => {
      const target = pendingFocusRef.current;

      if (target !== null && target.isConnected) {
        target.focus({ preventScroll: true });
      }

      pendingFocusRef.current = null;
    }, [stack]);

    const contextValue = useMemo(
      () => ({
        stack,
        restore_focus: (opener: HTMLElement | null) => {
          pendingFocusRef.current = opener;
        },
      }),
      [stack]
    );

    return <Context.Provider value={contextValue}>{children}</Context.Provider>;
  };

  const useSidePeekNavigation = (): SidePeekNavigation<TSidePeekMap> => {
    const eventSystem = useEventSystem();
    const { stack } = useSidePeekContext();
    const emitter = eventSystem.fetchOrCreateEventEmitter<SidePeekEventMap>(
      SidePeekEventEmitterName.SIDE_PEEK
    );
    const makeEntry = (invocation: SidePeekInvocation<TSidePeekMap>) => {
      const resolved = resolve(...invocation);
      const opener = invocation[2];
      instanceSequence += 1;

      return {
        ...resolved,
        instance_key: `side-peek-${instanceSequence}`,
        opener,
      };
    };

    return {
      push: (...invocation) =>
        emitter.emit(SidePeekEvent.PUSH, { entry: makeEntry(invocation) }),
      replace: (...invocation) =>
        emitter.emit(SidePeekEvent.REPLACE, { entry: makeEntry(invocation) }),
      pop: () => emitter.emit(SidePeekEvent.POP, { requested: true }),
      closeAll: () =>
        emitter.emit(SidePeekEvent.CLOSE_ALL, { requested: true }),
      stackDepth: stack.length,
    };
  };

  const SidePeekHost = () => {
    const { stack } = useSidePeekContext();
    const { pop } = useSidePeekNavigation();
    const shouldReduceMotion = useReducedMotion();
    const panelRefs = useRef(new Map<string, HTMLDivElement>());

    useEffect(() => {
      const top = stack[stack.length - 1];

      if (top !== undefined) {
        panelRefs.current.get(top.instance_key)?.focus({ preventScroll: true });
      }
    }, [stack]);

    const closeTop = () => {
      const top = stack[stack.length - 1];

      if (top?.dismissible) {
        pop();
      }
    };

    const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
      if (event.key === 'Escape') {
        closeTop();

        return;
      }

      if (event.key !== 'Tab') {
        return;
      }

      const top = stack[stack.length - 1];
      const panel =
        top === undefined ? undefined : panelRefs.current.get(top.instance_key);
      const focusableCandidates = panel?.querySelectorAll<HTMLElement>(
        'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], [contenteditable]:not([contenteditable="false"]), [tabindex]'
      );
      const focusable = Array.from(focusableCandidates ?? []).filter(
        (candidate) => {
          if (candidate.closest('[inert]') !== null) {
            return false;
          }

          if (candidate.closest('[aria-hidden="true"]') !== null) {
            return false;
          }

          if (
            candidate instanceof HTMLInputElement &&
            candidate.type === 'hidden'
          ) {
            return false;
          }

          return candidate.tabIndex >= 0;
        }
      );

      if (focusable.length === 0) {
        event.preventDefault();
        panel?.focus();

        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && event.target === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && event.target === last) {
        event.preventDefault();
        first.focus();
      }
    };

    if (stack.length === 0) {
      return null;
    }

    const duration = shouldReduceMotion === true ? 0 : 0.3;

    return (
      <div className="fixed inset-0 z-[70]" onKeyDownCapture={handleKeyDown}>
        <button
          type="button"
          aria-label="Close side peek"
          onClick={closeTop}
          className="absolute inset-0 bg-black/40"
        />
        <AnimatePresence initial={false}>
          {stack.map((entry, index) => {
            const isTop = index === stack.length - 1;

            return (
              <motion.div
                key={entry.instance_key}
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ duration, ease: 'easeOut' }}
                aria-hidden={!isTop}
                inert={!isTop}
                className={clsx('absolute inset-y-0 right-0', {
                  'pointer-events-auto': isTop,
                  'pointer-events-none': !isTop,
                })}
              >
                <SidePeek
                  title={entry.title}
                  on_close={closeTop}
                  panel_ref={(element) => {
                    if (element === null) {
                      panelRefs.current.delete(entry.instance_key);
                    } else {
                      panelRefs.current.set(entry.instance_key, element);
                    }
                  }}
                >
                  {entry.render_content()}
                </SidePeek>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    );
  };

  return { SidePeekProvider, SidePeekHost, useSidePeekNavigation };
};

export { createSidePeekManager };
