enum NavigationRoutes {
  HOME = '/',
  ABOUT = '/about',
  UPDATES = '/updates',
  HELP = '/help',
  LOGIN = '/login',
  REGISTER = '/register',
  GOOGLE_AUTH_CALLBACK = '/auth/google/callback',

  // Protected Routes
  ONBOARDING = '/onboarding',
  DASHBOARD = '/dashboard',
  PLAN_FUTURE_EXPENSES = '/dashboard/plan-future-expenses',
  DEBT_PROFILES = '/dashboard/debt-profiles',
  PAYDAY = '/dashboard/payday/:periodId',
  PROFILE = '/profile',
  SETTINGS = '/settings',
}

export { NavigationRoutes };
