import { toast as hotToast } from 'react-hot-toast';

export const useToast = () => {
  return {
    success: (message: string) => {
      hotToast.success(message, {
        duration: 4000,
        position: 'top-right',
      });
    },
    error: (message: string) => {
      hotToast.error(message, {
        duration: 4000,
        position: 'top-right',
      });
    },
    info: (message: string) => {
      hotToast(message, {
        duration: 4000,
        position: 'top-right',
      });
    },
  };
};
