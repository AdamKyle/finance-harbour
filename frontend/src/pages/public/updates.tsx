import SlidingContentPanel from 'ui/panels/sliding-content-panel';

const Updates = () => {
  return (
    <SlidingContentPanel title="Version History">
      <div className="space-y-6">
        <p className="text-storm-dust-700 dark:text-storm-dust-200 leading-7">
          This page will show product updates, release notes, and new Finance
          Harbour features.
        </p>
      </div>
    </SlidingContentPanel>
  );
};

export default Updates;
