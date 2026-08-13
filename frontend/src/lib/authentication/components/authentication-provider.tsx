import { ReactNode, useCallback, useEffect } from 'react';

import AuthenticationProviderProps from './types/authentication-provider-props';

import { useApiHandler } from 'lib/api-handler/hooks/use-api-handler';
import { useAuthenticatedUser } from 'lib/authentication/api/hooks/use-authenticated-user';
import { AuthenticationContext } from 'lib/authentication/authentication-context';
import { AuthenticationEvent } from 'lib/authentication/events/authentication-event';
import { AuthenticationEventEmitterName } from 'lib/authentication/events/authentication-event-emitter-name';
import { AuthenticationEventMap } from 'lib/authentication/events/authentication-event-map';
import SessionExpiredEventPayload from 'lib/authentication/events/definitions/session-expired-event-payload';
import { useEventSystem } from 'lib/event-system/hooks/use-event-system';

export const AuthenticationProvider = (
  props: AuthenticationProviderProps
): ReactNode => {
  const { authenticatedUser, error, loading, setAuthenticatedUser } =
    useAuthenticatedUser();
  const { apiHandler } = useApiHandler();
  const eventSystem = useEventSystem();

  const clearAuthenticatedUser = useCallback(() => {
    apiHandler.clearCsrfToken();
    setAuthenticatedUser(null);
  }, [apiHandler, setAuthenticatedUser]);

  useEffect(() => {
    const emitter =
      eventSystem.fetchOrCreateEventEmitter<AuthenticationEventMap>(
        AuthenticationEventEmitterName.AUTHENTICATION
      );
    const handleSessionExpired = (_payload: SessionExpiredEventPayload) => {
      clearAuthenticatedUser();
    };

    emitter.on(AuthenticationEvent.SESSION_EXPIRED, handleSessionExpired);

    return () => {
      emitter.off(AuthenticationEvent.SESSION_EXPIRED, handleSessionExpired);
    };
  }, [clearAuthenticatedUser, eventSystem]);

  return (
    <AuthenticationContext.Provider
      value={{
        authenticatedUser,
        clearAuthenticatedUser,
        error,
        loading,
        setAuthenticatedUser,
      }}
    >
      {props.children}
    </AuthenticationContext.Provider>
  );
};
