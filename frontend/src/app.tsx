import 'reflect-metadata';

import React from 'react';
import { createRoot, Root } from 'react-dom/client';
import { BrowserRouter } from 'react-router';

import FinanceHarbourApplication from './finance-harbour-application';

import { ApiHandlerProvider } from 'lib/api-handler/components/api-handler-provider';
import { AuthenticationProvider } from 'lib/authentication/components/authentication-provider';
import { EventSystemProvider } from 'lib/event-system/components/event-system-provider';
import { ServiceContainer } from 'lib/service-container-provider/service-container';

import { DarkModeProvider } from 'ui/dark-mode-toggle/components/dark-mode-provider';

import 'styles/styles.css';

class FinanceHarbourRootElement extends HTMLElement {
  private reactRoot: Root | null = null;

  connectedCallback(): void {
    if (this.reactRoot !== null) {
      return;
    }

    this.reactRoot = createRoot(this);
    this.reactRoot.render(
      <React.StrictMode>
        <BrowserRouter>
          <ServiceContainer>
            <EventSystemProvider>
              <DarkModeProvider>
                <ApiHandlerProvider>
                  <AuthenticationProvider>
                    <FinanceHarbourApplication />
                  </AuthenticationProvider>
                </ApiHandlerProvider>
              </DarkModeProvider>
            </EventSystemProvider>
          </ServiceContainer>
        </BrowserRouter>
      </React.StrictMode>
    );
  }

  disconnectedCallback(): void {
    this.reactRoot?.unmount();
    this.reactRoot = null;
  }
}

if (globalThis.customElements.get('finance-harbour-root') === undefined) {
  globalThis.customElements.define(
    'finance-harbour-root',
    FinanceHarbourRootElement
  );
}
