import clsx from 'clsx';
import React, { ChangeEvent } from 'react';

import profileImage2 from 'assets/profile-images/profile-image-2.png';
import profileImage3 from 'assets/profile-images/profile-image-3.png';
import profileImage4 from 'assets/profile-images/profile-image-4.png';
import profileImageOne from 'assets/profile-images/profile-image-one.png';

import ProfileStepProps from 'components/pages/onboarding/types/profile-step-props';

import Input from 'ui/form-elements/input';

const ProfileStep = ({ request, setRequest, error }: ProfileStepProps) => {
  const defaultPhoto = {
    id: 'avatar-d',
    label: 'Animated young man at Finance Harbour',
    src: profileImage4,
  };
  const profilePhotos = [
    {
      id: 'avatar-a',
      label: 'Animated woman with long dark hair at Finance Harbour',
      src: profileImageOne,
    },
    {
      id: 'avatar-b',
      label: 'Animated man with dark hair at Finance Harbour',
      src: profileImage2,
    },
    {
      id: 'avatar-c',
      label: 'Animated woman with curly hair at Finance Harbour',
      src: profileImage3,
    },
    defaultPhoto,
  ];

  const selected =
    profilePhotos.find((photo) => photo.id === request.profile_photo) ??
    defaultPhoto;

  const alternates = profilePhotos.filter((photo) => photo.id !== selected.id);

  const handleSelect = (id: string) => {
    setRequest({ ...request, profile_photo: id });
  };

  const handleNicknameChange = (event: ChangeEvent<HTMLInputElement>) => {
    setRequest({ ...request, nickname: event.target.value });
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-2">
        <p className="text-storm-dust-600 dark:text-storm-dust-300 text-sm">
          Lets start with an avatar and nickname. Don't worry, only you can see
          these details. Next we'll dive right into the debt profile setup and
          help you tackle those debts.
        </p>
      </div>

      <fieldset>
        <legend className="text-storm-dust-800 dark:text-storm-dust-100 mb-3 text-sm font-semibold">
          Profile avatar (optional)
        </legend>

        <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:justify-center">
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-1 sm:grid-rows-3">
            {alternates.map((photo) => (
              <button
                key={photo.id}
                type="button"
                aria-pressed={false}
                aria-label={`Select ${photo.label} avatar`}
                onClick={() => handleSelect(photo.id)}
                className={clsx(
                  'h-20 w-20 rounded-lg transition-transform duration-200',
                  'hover:scale-105 focus-visible:scale-105',
                  'focus-visible:ring-blue-bell-500 focus-visible:ring-2',
                  'focus-visible:ring-offset-2 focus-visible:outline-none'
                )}
              >
                <img
                  src={photo.src}
                  alt={`${photo.label} avatar`}
                  className="aspect-square h-full w-full rounded-lg object-cover"
                />
              </button>
            ))}
          </div>

          <button
            type="button"
            aria-pressed={true}
            aria-label={`${selected.label} avatar, selected`}
            onClick={() => handleSelect(selected.id)}
            className={clsx(
              'ring-blue-bell-500 aspect-square w-full max-w-64 rounded-lg ring-4',
              'ring-offset-2 focus-visible:ring-4 focus-visible:outline-none',
              'sm:h-64 sm:w-64'
            )}
          >
            <img
              src={selected.src}
              alt={`${selected.label} avatar`}
              className="aspect-square h-full w-full rounded-lg object-cover"
            />
          </button>
        </div>
      </fieldset>

      <Input
        id="onboarding-nickname"
        label="Nickname"
        name="nickname"
        type="text"
        placeholder="e.g. Alex"
        value={request.nickname}
        error={error}
        has_error={error !== undefined}
        required
        onChange={handleNicknameChange}
      />
    </div>
  );
};

export default ProfileStep;
