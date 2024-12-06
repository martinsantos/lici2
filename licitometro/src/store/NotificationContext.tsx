import * as React from 'react';
import { createContext, useContext } from 'react';
import toast from 'react-hot-toast';

interface NotificationContextType {
  showNotification: (message: string, type: 'success' | 'error' | 'info') => void;
}

// Create a noop function for the default value
const noop = () => {};

// Create the context with a default value
const NotificationContext = createContext<NotificationContextType>({
  showNotification: noop,
});

// Custom hook to use the notification context
export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
}

// Provider component
export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const showNotification = React.useCallback((message: string, type: 'success' | 'error' | 'info') => {
    switch (type) {
      case 'success':
        toast.success(message);
        break;
      case 'error':
        toast.error(message);
        break;
      case 'info':
        toast(message);
        break;
    }
  }, []);

  const value = React.useMemo(() => ({ showNotification }), [showNotification]);

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
