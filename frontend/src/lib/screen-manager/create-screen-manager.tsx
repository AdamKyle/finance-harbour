import clsx from 'clsx';
import {
  AnimatePresence,
  motion,
  useIsPresent,
  useReducedMotion,
} from 'motion/react';
import {
  createContext,
  useContext,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type FocusEvent,
  type KeyboardEvent,
} from 'react';

import { BindScreenMode } from './hooks/definitions/use-bind-screen-params';
import { createBindingHostComponent } from './screen-binding-host';
import { NavigationType } from './types/navigation-type';
import { RegistryType } from './types/registry-type';
import { ScreenContextValueType } from './types/screen-context-value-type';
import { ScreenEntryViewPropsType } from './types/screen-entry-view-props-type';
import { ScreenInvocationType } from './types/screen-invocation-type';
import ScreenManagerProviderProps from './types/screen-manager-provider-props';
import { StackEntryType } from './types/stack-entry-type';
import {
  normalMotionProps,
  reducedMotionProps,
} from './variants/animation-variants';

const isDisabledFormElement = (element: HTMLElement): boolean => {
  if (element instanceof HTMLButtonElement) {
    return element.disabled;
  }

  if (element instanceof HTMLInputElement) {
    return element.disabled;
  }

  if (element instanceof HTMLSelectElement) {
    return element.disabled;
  }

  if (element instanceof HTMLTextAreaElement) {
    return element.disabled;
  }

  if (element instanceof HTMLFieldSetElement) {
    return element.disabled;
  }

  return false;
};

const isNaturallyFocusableElement = (element: HTMLElement): boolean => {
  if (element instanceof HTMLAnchorElement) {
    return element.hasAttribute('href');
  }

  if (element instanceof HTMLButtonElement) {
    return true;
  }

  if (element instanceof HTMLInputElement) {
    return element.type !== 'hidden';
  }

  if (element instanceof HTMLSelectElement) {
    return true;
  }

  if (element instanceof HTMLTextAreaElement) {
    return true;
  }

  return element.isContentEditable;
};

const isElementFocusable = (element: HTMLElement): boolean => {
  if (!element.isConnected) {
    return false;
  }

  if (element instanceof HTMLInputElement && element.type === 'hidden') {
    return false;
  }

  if (isDisabledFormElement(element)) {
    return false;
  }

  if (element.closest('fieldset:disabled')) {
    return false;
  }

  if (element.closest('[inert]')) {
    return false;
  }

  if (element.closest('[hidden]')) {
    return false;
  }

  if (element.closest('[aria-hidden="true"]')) {
    return false;
  }

  const computedStyle = globalThis.getComputedStyle(element);

  if (computedStyle.display === 'none') {
    return false;
  }

  if (computedStyle.visibility === 'hidden') {
    return false;
  }

  if (isNaturallyFocusableElement(element)) {
    return true;
  }

  return element.tabIndex >= 0;
};

const createScreenManager = <TScreenMap,>(
  registry: RegistryType<TScreenMap>
) => {
  const makeEntry = (
    invocation: ScreenInvocationType<TScreenMap>,
    instanceKeyCounterRef: { current: number },
    ownerKey?: string,
    opener: HTMLElement | null = null
  ): StackEntryType<TScreenMap> => {
    const resolved = registry(...invocation);
    const instanceKey = ownerKey ?? String(++instanceKeyCounterRef.current);

    return {
      instanceKey,
      screenName: resolved.screenName,
      renderContent: resolved.renderContent,
      dismissible: resolved.dismissible,
      bindingOwnerKey: ownerKey,
      openedByElement: opener,
    };
  };

  const Context = createContext<ScreenContextValueType<TScreenMap> | null>(
    null
  );

  const useCtx = (): ScreenContextValueType<TScreenMap> => {
    const ctx = useContext(Context);

    if (!ctx) {
      throw new Error(
        'Screen manager hooks must be used within ScreenManagerProvider'
      );
    }

    return ctx;
  };

  const ScreenManagerProvider = ({ children }: ScreenManagerProviderProps) => {
    const [stack, setStack] = useState<StackEntryType<TScreenMap>[]>([]);
    const pendingFocusRef = useRef<HTMLElement | null>(null);
    const lastFocusedElementRef = useRef<HTMLElement | null>(null);
    const instanceKeyCounterRef = useRef(0);

    useEffect(() => {
      const target = pendingFocusRef.current;

      if (target === null) {
        return;
      }

      if (isElementFocusable(target)) {
        target.focus({ preventScroll: true });
      }

      pendingFocusRef.current = null;
    }, [stack]);

    const value = useMemo(
      () => ({
        stack,
        setStack,
        pendingFocusRef,
        instanceKeyCounterRef,
        lastFocusedElementRef,
      }),
      [stack, setStack, pendingFocusRef, instanceKeyCounterRef]
    );

    const handleFocusCapture = (event: FocusEvent<HTMLDivElement>) => {
      if (event.target instanceof HTMLElement) {
        lastFocusedElementRef.current = event.target;
      }
    };

    return (
      <Context.Provider value={value}>
        <div onFocusCapture={handleFocusCapture}>{children}</div>
      </Context.Provider>
    );
  };

  const useScreenNavigation = (): NavigationType<TScreenMap> => {
    const {
      stack,
      setStack,
      pendingFocusRef,
      instanceKeyCounterRef,
      lastFocusedElementRef,
    } = useCtx();

    return useMemo(
      () => ({
        navigateTo: (...invocation: ScreenInvocationType<TScreenMap>) => {
          const opener = lastFocusedElementRef.current;
          const newEntry = makeEntry(
            invocation,
            instanceKeyCounterRef,
            undefined,
            opener
          );
          setStack((prev) => [...prev, newEntry]);
        },
        replaceWith: (...invocation: ScreenInvocationType<TScreenMap>) => {
          let existingOpener: HTMLElement | null = null;

          if (stack.length > 0) {
            existingOpener = stack[stack.length - 1].openedByElement;
          }
          const newEntry = makeEntry(
            invocation,
            instanceKeyCounterRef,
            undefined,
            existingOpener
          );
          setStack((prev) => {
            if (prev.length === 0) {
              return [newEntry];
            }
            return [...prev.slice(0, -1), newEntry];
          });
        },
        resetTo: (...invocation: ScreenInvocationType<TScreenMap>) => {
          setStack([makeEntry(invocation, instanceKeyCounterRef)]);
        },
        pop: (count: number = 1) => {
          let focusTarget: HTMLElement | null = null;
          let remaining = count;
          let idx = stack.length - 1;

          while (remaining > 0 && idx >= 0) {
            const entry = stack[idx];

            if (!entry.dismissible) {
              break;
            }

            focusTarget = entry.openedByElement;
            idx--;
            remaining--;
          }

          pendingFocusRef.current = focusTarget;

          setStack((prev) => {
            const newStack = [...prev];
            let rem = count;

            while (rem > 0 && newStack.length > 0) {
              if (!newStack[newStack.length - 1].dismissible) {
                break;
              }

              newStack.pop();
              rem--;
            }

            return newStack;
          });
        },
        stackDepth: stack.length,
      }),
      [
        stack,
        setStack,
        pendingFocusRef,
        instanceKeyCounterRef,
        lastFocusedElementRef,
      ]
    );
  };

  const useBindScreen = (
    invocation: ScreenInvocationType<TScreenMap>,
    mode: BindScreenMode
  ) => {
    const ownerKey = useId();
    const { setStack, instanceKeyCounterRef } = useCtx();

    useLayoutEffect(() => {
      const newEntry = makeEntry(invocation, instanceKeyCounterRef, ownerKey);

      setStack((prev) => {
        const existingIndex = prev.findIndex(
          (e) => e.bindingOwnerKey === ownerKey
        );

        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = newEntry;
          return updated;
        }

        if (mode === 'reset') {
          const otherBoundEntries = prev.filter(
            (entry) => entry.bindingOwnerKey !== ownerKey
          );

          return [newEntry, ...otherBoundEntries];
        }

        if (mode === 'replace') {
          if (prev.length === 0) {
            return [newEntry];
          }

          return [...prev.slice(0, -1), newEntry];
        }

        return [...prev, newEntry];
      });
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [ownerKey, mode, setStack, instanceKeyCounterRef, ...invocation]);

    useLayoutEffect(() => {
      return () => {
        setStack((prev) => prev.filter((e) => e.bindingOwnerKey !== ownerKey));
      };
    }, [ownerKey, setStack]);
  };

  const ScreenEntryView = ({
    entry,
    isActive,
    setRef,
  }: ScreenEntryViewPropsType<TScreenMap>) => {
    const isPresent = useIsPresent();
    const isInteractive = isActive && isPresent;
    const getAriaHidden = () => {
      if (isInteractive) {
        return undefined;
      }

      return true;
    };
    const getInert = () => {
      if (isInteractive) {
        return undefined;
      }

      return true;
    };
    const getPointerEvents = () => {
      if (isInteractive) {
        return undefined;
      }

      return 'none';
    };

    return (
      <div
        ref={setRef}
        tabIndex={-1}
        className="min-h-full outline-none"
        aria-hidden={getAriaHidden()}
        inert={getInert()}
        style={{ pointerEvents: getPointerEvents() }}
      >
        {entry.renderContent()}
      </div>
    );
  };

  const ScreenHost = () => {
    const { stack, setStack, pendingFocusRef } = useCtx();
    const shouldReduceMotion = useReducedMotion();
    const containerRefsMap = useRef(new Map<string, HTMLDivElement | null>());

    useEffect(() => {
      if (stack.length === 0) {
        return;
      }

      const top = stack[stack.length - 1];
      const container = containerRefsMap.current.get(top.instanceKey);

      if (container) {
        container.focus({ preventScroll: true });
      }
    }, [stack]);

    const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
      if (event.key !== 'Escape') {
        return;
      }

      const top = stack[stack.length - 1];

      if (!top?.dismissible) {
        return;
      }

      pendingFocusRef.current = top.openedByElement;

      setStack((prev) => {
        if (prev.length === 0 || !prev[prev.length - 1].dismissible) {
          return prev;
        }

        return prev.slice(0, -1);
      });
    };

    const getMotionProps = () => {
      if (shouldReduceMotion) {
        return reducedMotionProps;
      }

      return normalMotionProps;
    };
    const motionProps = getMotionProps();

    const getHostClassName = () => {
      if (stack.length === 0) {
        return undefined;
      }

      return 'relative min-w-0 w-full';
    };

    const renderScreens = () =>
      stack.map((entry, index) => {
        const isActive = index === stack.length - 1;
        const isBaseScreen = index === 0;

        return (
          <motion.div
            key={entry.instanceKey}
            initial={motionProps.initial}
            animate={motionProps.animate}
            exit={motionProps.exit}
            transition={motionProps.transition}
            className={clsx({
              relative: isBaseScreen,
              'absolute inset-0 overflow-x-hidden overflow-y-auto':
                !isBaseScreen,
            })}
          >
            <ScreenEntryView
              entry={entry}
              isActive={isActive}
              setRef={(el) => {
                if (el) {
                  containerRefsMap.current.set(entry.instanceKey, el);
                } else {
                  containerRefsMap.current.delete(entry.instanceKey);
                }
              }}
            />
          </motion.div>
        );
      });

    return (
      <div className={getHostClassName()} onKeyDownCapture={handleKeyDown}>
        <AnimatePresence>{renderScreens()}</AnimatePresence>
      </div>
    );
  };

  const ScreenBindingHost =
    createBindingHostComponent<TScreenMap>(useBindScreen);

  return {
    ScreenManagerProvider,
    ScreenHost,
    ScreenBindingHost,
    useScreenNavigation,
    useBindScreen,
  };
};

export { createScreenManager };
