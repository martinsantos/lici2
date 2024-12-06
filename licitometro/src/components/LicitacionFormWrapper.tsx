import React, { useState } from 'react';
import { AppProvider } from '../store/AppContext';
import { NotificationProvider } from '../store/NotificationContext';
import LicitacionForm from './LicitacionForm';
import { Toaster } from 'react-hot-toast';

interface LicitacionFormWrapperProps {
  onSuccess?: () => void;
  initialData?: any;
  isEditing?: boolean;
}

const LicitacionFormWrapper: React.FC<LicitacionFormWrapperProps> = ({ onSuccess, initialData, isEditing = false }) => {
  const [isOpen, setIsOpen] = useState(isEditing);

  return (
    <AppProvider>
      <NotificationProvider>
        <div>
          {!isEditing && (
            <button
              onClick={() => setIsOpen(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Nueva Licitación
            </button>
          )}

          {(isOpen || isEditing) && (
            <div className={`${isEditing ? '' : 'fixed inset-0 z-50'} overflow-y-auto`}>
              <div className={`flex ${isEditing ? '' : 'min-h-screen'} items-center justify-center p-4`}>
                {!isEditing && (
                  <div 
                    className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
                    onClick={() => !isEditing && setIsOpen(false)} 
                  />
                )}
                <div className={`relative bg-white rounded-lg shadow-xl ${isEditing ? 'w-full' : 'max-w-2xl w-full'} p-6`}>
                  <Toaster position="top-right" />
                  {!isEditing && (
                    <div className="absolute right-4 top-4">
                      <button
                        onClick={() => setIsOpen(false)}
                        className="text-gray-400 hover:text-gray-500"
                      >
                        <span className="sr-only">Cerrar</span>
                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  )}
                  <LicitacionForm 
                    onSuccess={() => {
                      if (!isEditing) {
                        setIsOpen(false);
                      }
                      if (onSuccess) {
                        onSuccess();
                      }
                      // Redirect back to the licitación view page after successful edit
                      if (isEditing && initialData?.id) {
                        window.location.href = `/licitaciones/${initialData.id}`;
                      }
                    }} 
                    initialData={initialData}
                    isEditing={isEditing}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </NotificationProvider>
    </AppProvider>
  );
};

export default LicitacionFormWrapper;
