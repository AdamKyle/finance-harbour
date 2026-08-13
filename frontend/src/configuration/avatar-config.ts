import profileImage2 from 'assets/profile-images/profile-image-2.png';
import profileImage3 from 'assets/profile-images/profile-image-3.png';
import profileImage4 from 'assets/profile-images/profile-image-4.png';
import profileImageOne from 'assets/profile-images/profile-image-one.png';

export interface AvatarConfig {
  id: string;
  label: string;
  src: string;
}

export const AVATAR_OPTIONS: AvatarConfig[] = [
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
  {
    id: 'avatar-d',
    label: 'Animated young man at Finance Harbour',
    src: profileImage4,
  },
];

export const getAvatarById = (id: string): AvatarConfig | null =>
  AVATAR_OPTIONS.find((avatar) => avatar.id === id) ?? null;
