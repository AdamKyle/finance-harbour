import { Route, Routes } from 'react-router';

import AuthorizedLayout from './layout/authorized-layout';
import PublicLayout from './layout/public-layout';
import LandingPage from './pages/landing-page';
import DashboardPage from './pages/protected/dashboard';
import DebtProfilesPage from './pages/protected/debt-profiles';
import HelpPage from './pages/protected/help';
import Onboard from './pages/protected/onboard';
import PaydayPage from './pages/protected/payday';
import PlanFutureExpensesPage from './pages/protected/plan-future-expenses';
import Profile from './pages/protected/profile';
import Settings from './pages/protected/settings';
import UpdatesPage from './pages/protected/updates';
import About from './pages/public/about';
import GoogleAuthCallback from './pages/public/google-auth-callback';
import Help from './pages/public/help';
import Login from './pages/public/login';
import Register from './pages/public/register';
import Updates from './pages/public/updates';
import AuthenticatedPublicRedirectRoute from './react-router/components/authenticated-public-redirect-route';
import CompletedRoute from './react-router/components/completed-route';
import IncompleteRoute from './react-router/components/incomplete-route';
import ProtectedRoute from './react-router/components/protected-route';
import { NavigationRoutes } from './react-router/enums/navigation-routes';

import { useAuthentication } from 'lib/authentication/hooks/use-authentication';

const FinanceHarbourApplication = () => {
  const { authenticatedUser, loading } = useAuthentication();

  if (loading) {
    return null;
  }

  if (authenticatedUser) {
    return (
      <Routes>
        <Route element={<PublicLayout />}>
          <Route element={<AuthenticatedPublicRedirectRoute />}>
            <Route path={NavigationRoutes.HOME} element={<LandingPage />} />
            <Route path={NavigationRoutes.LOGIN} element={<Login />} />
            <Route path={NavigationRoutes.REGISTER} element={<Register />} />
          </Route>

          <Route path={NavigationRoutes.ABOUT} element={<About />} />

          <Route
            path={NavigationRoutes.GOOGLE_AUTH_CALLBACK}
            element={<GoogleAuthCallback />}
          />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<AuthorizedLayout />}>
            <Route path={NavigationRoutes.HELP} element={<HelpPage />} />
            <Route path={NavigationRoutes.UPDATES} element={<UpdatesPage />} />

            <Route element={<IncompleteRoute />}>
              <Route path={NavigationRoutes.ONBOARDING} element={<Onboard />} />
            </Route>

            <Route element={<CompletedRoute />}>
              <Route
                path={NavigationRoutes.DASHBOARD}
                element={<DashboardPage />}
              >
                <Route
                  path={NavigationRoutes.PLAN_FUTURE_EXPENSES}
                  element={<PlanFutureExpensesPage />}
                />
                <Route
                  path={NavigationRoutes.DEBT_PROFILES}
                  element={<DebtProfilesPage />}
                />
                <Route
                  path={NavigationRoutes.PAYDAY}
                  element={<PaydayPage />}
                />
              </Route>
              <Route path={NavigationRoutes.PROFILE} element={<Profile />} />
              <Route path={NavigationRoutes.SETTINGS} element={<Settings />} />
            </Route>
          </Route>
        </Route>
      </Routes>
    );
  }

  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route element={<AuthenticatedPublicRedirectRoute />}>
          <Route path={NavigationRoutes.HOME} element={<LandingPage />} />
          <Route path={NavigationRoutes.LOGIN} element={<Login />} />
          <Route path={NavigationRoutes.REGISTER} element={<Register />} />
        </Route>

        <Route path={NavigationRoutes.ABOUT} element={<About />} />
        <Route path={NavigationRoutes.HELP} element={<Help />} />
        <Route path={NavigationRoutes.UPDATES} element={<Updates />} />

        <Route
          path={NavigationRoutes.GOOGLE_AUTH_CALLBACK}
          element={<GoogleAuthCallback />}
        />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AuthorizedLayout />}>
          <Route element={<IncompleteRoute />}>
            <Route path={NavigationRoutes.ONBOARDING} element={<Onboard />} />
          </Route>

          <Route element={<CompletedRoute />}>
            <Route
              path={NavigationRoutes.DASHBOARD}
              element={<DashboardPage />}
            >
              <Route
                path={NavigationRoutes.PLAN_FUTURE_EXPENSES}
                element={<PlanFutureExpensesPage />}
              />
              <Route
                path={NavigationRoutes.DEBT_PROFILES}
                element={<DebtProfilesPage />}
              />
              <Route path={NavigationRoutes.PAYDAY} element={<PaydayPage />} />
            </Route>
            <Route path={NavigationRoutes.PROFILE} element={<Profile />} />
            <Route path={NavigationRoutes.SETTINGS} element={<Settings />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
};

export default FinanceHarbourApplication;
