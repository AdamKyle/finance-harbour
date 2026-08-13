import { BindScreenMode } from 'lib/screen-manager/hooks/definitions/use-bind-screen-params';
import { ScreenInvocationType } from 'lib/screen-manager/types/screen-invocation-type';

export interface ScreenBindingHostProps<TScreenMap> {
  invocation: ScreenInvocationType<TScreenMap>;
  mode?: BindScreenMode;
}
