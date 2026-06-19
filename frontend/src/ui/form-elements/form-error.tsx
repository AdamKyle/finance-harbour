import type FormErrorProps from './types/form-error-props';

const FormError = ({ id, message }: FormErrorProps) => {
  if (!message) {
    return null;
  }

  return (
    <p
      className="text-persian-plum-600 dark:text-persian-plum-400 text-sm font-medium"
      id={id}
      role="alert"
    >
      {message}
    </p>
  );
};

export default FormError;
