import type NavigationItemDefinition from 'router/public-routes/definitions/navigation-item-definition';

export default interface BaseMobileNavigationProps {
  isMenuOpen: boolean;
  mobileMenuId: string;
  navigationItems: NavigationItemDefinition[];
  shouldReduceMotion: boolean | null;
  isAuthenticated: boolean;
  isAuthenticationLoading: boolean;
  onCloseMenu: () => void;
  onLogin: () => void;
  onRegister: () => void;
}
