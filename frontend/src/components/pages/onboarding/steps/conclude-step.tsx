import React from 'react';

const ConcludeStep = () => {
  return (
    <div className="flex flex-col items-center gap-6 py-4 text-center">
      <div aria-hidden="true" className="text-5xl">
        &#127881;
      </div>
      <h3 className="text-storm-dust-900 dark:text-storm-dust-50 text-2xl font-bold">
        You&apos;re all set!
      </h3>
      <p className="text-storm-dust-600 dark:text-storm-dust-300 max-w-sm text-sm">
        Your profile is complete. Click <strong>Finish</strong> to start using
        Finance Harbour and take control of your finances.
      </p>
    </div>
  );
};

export default ConcludeStep;
