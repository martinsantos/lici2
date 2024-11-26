import React, { useState } from 'react';
import { TemplateList } from './TemplateList';
import { TemplateEditor } from './TemplateEditor';
import { useTemplateStore } from '../store/templateStore';
import type { ScrapingTemplate } from '../types/recon';

const TemplateManager: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const selectedTemplate = useTemplateStore(state => state.selectedTemplate);
  const selectTemplate = useTemplateStore(state => state.selectTemplate);

  const handleCreateNew = () => {
    selectTemplate(null);
    setIsEditing(true);
  };

  const handleEdit = (template: ScrapingTemplate) => {
    setIsEditing(true);
  };

  const handleClose = () => {
    selectTemplate(null);
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      {!isEditing ? (
        <div>
          <div className="mb-4">
            <button
              onClick={handleCreateNew}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Crear Nueva Plantilla
            </button>
          </div>
          <TemplateList onEdit={handleEdit} />
        </div>
      ) : (
        <div>
          <div className="mb-4">
            <button
              onClick={handleClose}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Volver a la Lista
            </button>
          </div>
          <TemplateEditor onClose={handleClose} />
        </div>
      )}
    </div>
  );
};

export default TemplateManager;
