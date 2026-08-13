import { BindScreenMode } from './hooks/definitions/use-bind-screen-params';
import { ScreenBindingHostProps } from './types/screen-binding-host-props';
import { ScreenInvocationType } from './types/screen-invocation-type';

export const createBindingHostComponent = <TScreenMap,>(
  useBindScreenFn: (
    invocation: ScreenInvocationType<TScreenMap>,
    mode: BindScreenMode
  ) => void
) => {
  const ScreenBindingHost = (props: ScreenBindingHostProps<TScreenMap>) => {
    const { invocation, mode = 'reset' } = props;

    useBindScreenFn(invocation, mode);

    return null;
  };

  return ScreenBindingHost;
};
