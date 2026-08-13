import { ReactNode, useId } from 'react';
import { useNavigate } from 'react-router';

import SectionWithTitleProps from './types/section-with-title-props';

import { NavigationRoutes } from 'router/enums/navigation-routes';
import { navigateToRoute } from 'router/utils/navigate-to-route';

import { ButtonVariant } from 'ui/buttons/enums/button-variant';
import IconButton from 'ui/buttons/icon-button';
import Card from 'ui/cards/card';

const SectionWithTitle = ({
  children,
  title,
  back_route = NavigationRoutes.HOME,
  back_state,
  on_back,
}: SectionWithTitleProps): ReactNode => {
  const navigate = useNavigate();
  const titleId = useId();

  const handleGoBack = () => {
    if (on_back !== undefined) {
      on_back();

      return;
    }

    if (back_state !== undefined) {
      void navigate(back_route, { state: back_state });

      return;
    }

    navigateToRoute(navigate, back_route);
  };

  const renderContent = () => {
    if (children === undefined) {
      return null;
    }

    return <Card>{children}</Card>;
  };

  return (
    <main className="bg-storm-dust-50 text-storm-dust-950 dark:bg-storm-dust-950 dark:text-storm-dust-50 flex-1 px-4 py-8 transition-colors sm:px-6 sm:py-12 lg:py-16">
      <section aria-labelledby={titleId} className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center gap-3 sm:mb-8">
          <IconButton
            icon="fa-solid fa-arrow-left"
            label={`Go back from ${title}`}
            variant={ButtonVariant.Default}
            on_click={handleGoBack}
            additional_css="shrink-0"
          />

          <h1
            id={titleId}
            className="text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl"
          >
            {title}
          </h1>
        </div>

        {renderContent()}
      </section>
    </main>
  );
};

export default SectionWithTitle;
