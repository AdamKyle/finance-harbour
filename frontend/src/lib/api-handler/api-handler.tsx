import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

import AxiosDefinition from './definitions/axios-definition';

export default class ApiHandler implements AxiosDefinition {
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
    const response: AxiosResponse<T> = await axios.get<T>(modifiedUrl, config);
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
    this.setRequestConfig(config);
    const modifiedUrl = this.addApiPrefix(url);
    const response: AxiosResponse<T> = await axios.post<T>(
      modifiedUrl,
      data,
      config
    );
    return response.data;
  }

  async patch<T, C, D>(
    url: string,
    data: D,
    config: AxiosRequestConfig & { params?: C } = {}
  ): Promise<T> {
    this.setRequestConfig(config);
    const modifiedUrl = this.addApiPrefix(url);
    const response: AxiosResponse<T> = await axios.patch<T>(
      modifiedUrl,
      data,
      config
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
   * Get the csrf token from the csrf cookie.
   *
   * @private
   */
  private getCsrfToken(): string {
    const cookie = document.cookie
      .split('; ')
      .find((cookieValue) => cookieValue.startsWith('csrftoken='));

    if (!cookie) {
      return '';
    }

    return decodeURIComponent(cookie.split('=')[1]);
  }

  /**
   * Set additional config and the csrf token.
   *
   * @param config
   * @private
   */
  private setRequestConfig(config: AxiosRequestConfig): void {
    const csrfToken = this.getCsrfToken();

    config.withCredentials = true;
    config.headers = {
      ...config.headers,
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    };

    if (csrfToken) {
      config.headers = {
        ...config.headers,
        'X-CSRFToken': csrfToken,
      };
    }
  }
}
