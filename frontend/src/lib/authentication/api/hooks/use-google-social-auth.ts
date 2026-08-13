import { useCallback } from 'react';

import UseGoogleSocialAuthDefinition from './definitions/use-google-social-auth-definition';

export const useGoogleSocialAuth = (): UseGoogleSocialAuthDefinition => {
  const redirectToGoogle = useCallback(() => {
    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');

    authUrl.searchParams.set(
      'client_id',
      import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID
    );
    authUrl.searchParams.set(
      'redirect_uri',
      import.meta.env.VITE_GOOGLE_OAUTH_REDIRECT_URI
    );
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('scope', 'openid email profile');
    authUrl.searchParams.set('access_type', 'online');

    globalThis.location.assign(authUrl.toString());
  }, []);

  return {
    redirectToGoogle,
  };
};
