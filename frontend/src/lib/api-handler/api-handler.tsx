import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

import AxiosDefinition from './definitions/axios-definition';

import CsrfResponseDefinition from 'lib/authentication/api/hooks/definitions/csrf-response-definition';
import { AuthenticationEvent } from 'lib/authentication/events/authentication-event';
import { AuthenticationEventEmitterName } from 'lib/authentication/events/authentication-event-emitter-name';
import { AuthenticationEventMap } from 'lib/authentication/events/authentication-event-map';
import { SessionExpiredReason } from 'lib/authentication/events/definitions/session-expired-event-payload';
import EventSystemDefinition from 'lib/event-system/definitions/event-system-definition';

export default class ApiHandler implements AxiosDefinition {
  private refreshRequest: Promise<void> | null = null;
  private csrfToken: string | null = null;

  constructor(private readonly eventSystem: EventSystemDefinition) {}

  setCsrfToken(token: string): void {
    this.csrfToken = token;
  }

  clearCsrfToken(): void {
    this.csrfToken = null;
  }

  async ensureCsrfToken(): Promise<string> {
    if (this.csrfToken !== null) {
      return this.csrfToken;
    }

    const response = await axios.get<CsrfResponseDefinition>(
      '/api/auth/csrf/',
      {
        withCredentials: true,
        headers: {
          Accept: 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
      }
    );
    this.setCsrfToken(response.data.csrfToken);

    return response.data.csrfToken;
  }

  /**
   * Get data from the server
   * @param url
   * @param config
   */
  async get<T>(
    url: string,
    config: AxiosRequestConfig & { params?: object } = {}
  ): Promise<T> {
    this.setRequestConfig(config);
    const modifiedUrl = this.addApiPrefix(url);
    const response = await this.sendWithRefresh<T>(
      () => axios.get<T>(modifiedUrl, config),
      modifiedUrl
    );
    return response.data;
  }

  /**
   * Post data to the server.
   *
   * @param url
   * @param data
   * @param config
   */
  async post<T, C, D>(
    url: string,
    data: D,
    config: AxiosRequestConfig & { params?: C } = {}
  ): Promise<T> {
    await this.ensureCsrfToken();
    this.setRequestConfig(config);
    const modifiedUrl = this.addApiPrefix(url);
    const response = await this.sendWithRefresh<T>(
      () => axios.post<T>(modifiedUrl, data, config),
      modifiedUrl
    );
    return response.data;
  }

  async patch<T, C, D>(
    url: string,
    data: D,
    config: AxiosRequestConfig & { params?: C } = {}
  ): Promise<T> {
    await this.ensureCsrfToken();
    this.setRequestConfig(config);
    const modifiedUrl = this.addApiPrefix(url);
    const response = await this.sendWithRefresh<T>(
      () => axios.patch<T>(modifiedUrl, data, config),
      modifiedUrl
    );
    return response.data;
  }

  /**
   * Add `/api` prefix to the URL if it's not already there.
   *
   * @param url
   * @private
   */
  private addApiPrefix(url: string): string {
    if (!url.startsWith('/api')) {
      return `/api${url}`;
    }
    return url;
  }

  /**
   * Set additional config and the csrf token.
   *
   * @param config
   * @private
   */
  private setRequestConfig(config: AxiosRequestConfig): void {
    config.withCredentials = true;
    config.headers = {
      ...config.headers,
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    };

    if (this.csrfToken !== null) {
      config.headers = {
        ...config.headers,
        'X-CSRFToken': this.csrfToken,
      };
    }
  }

  private async sendWithRefresh<T>(
    request: () => Promise<AxiosResponse<T>>,
    requestUrl = ''
  ): Promise<AxiosResponse<T>> {
    try {
      return await request();
    } catch (error) {
      if (
        !(error instanceof AxiosError) ||
        error.response?.status !== 401 ||
        !this.canRefreshRequest(requestUrl)
      ) {
        throw error;
      }

      try {
        await this.refreshAuthentication();
      } catch (refreshError) {
        this.emitSessionExpired(SessionExpiredReason.REFRESH_FAILED);

        throw refreshError;
      }

      try {
        return await request();
      } catch (retryError) {
        if (
          retryError instanceof AxiosError &&
          retryError.response?.status === 401
        ) {
          this.emitSessionExpired(SessionExpiredReason.REPEATED_UNAUTHORIZED);
        }

        throw retryError;
      }
    }
  }

  private canRefreshRequest(requestUrl: string): boolean {
    const nonRefreshableUrls = [
      '/api/auth/csrf/',
      '/api/auth/login/',
      '/api/auth/registration/',
      '/api/auth/social/google/',
      '/api/auth/token/refresh/',
    ];

    return !nonRefreshableUrls.includes(requestUrl);
  }

  private async refreshAuthentication(): Promise<void> {
    if (this.refreshRequest) {
      return this.refreshRequest;
    }

    const config: AxiosRequestConfig = {};
    this.setRequestConfig(config);

    this.refreshRequest = axios
      .post('/api/auth/token/refresh/', {}, config)
      .then(() => undefined)
      .finally(() => {
        this.refreshRequest = null;
      });

    return this.refreshRequest;
  }

  private emitSessionExpired(reason: SessionExpiredReason): void {
    const emitter =
      this.eventSystem.fetchOrCreateEventEmitter<AuthenticationEventMap>(
        AuthenticationEventEmitterName.AUTHENTICATION
      );

    emitter.emit(AuthenticationEvent.SESSION_EXPIRED, { reason });
  }
}
