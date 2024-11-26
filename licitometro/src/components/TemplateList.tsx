import React from 'react';
import { useTemplateStore } from '../store/templateStore';
import type { ScrapingTemplate } from '../types/recon';

interface TemplateListProps {
  onEdit: (template: ScrapingTemplate) => void;
}

export const TemplateList: React.FC<TemplateListProps> = ({ onEdit }) => {
  const templates = useTemplateStore(state => state.templates);
  const deleteTemplate = useTemplateStore(state => state.deleteTemplate);
  const setSelectedTemplate = useTemplateStore(state => state.setSelectedTemplate);

  const handleEdit = (template: ScrapingTemplate) => {
    setSelectedTemplate(template);
    onEdit(template);
  };

  const handleDelete = async (template: ScrapingTemplate) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar esta plantilla?')) {
      await deleteTemplate(template.id!);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((template) => (
        <div
          key={template.id}
          className="p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow"
        >
          <h3 className="text-lg font-semibold">{template.name}</h3>
          <p className="text-gray-600 text-sm mt-1">{template.description}</p>
          <p className="text-gray-500 text-sm mt-2">URL: {template.url}</p>
          <p className="text-gray-500 text-sm">
            Campos: {template.fields?.length || 0}
          </p>
          <div className="mt-4 flex space-x-2">
            <button
              onClick={() => handleEdit(template)}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
            >
              Editar
            </button>
            <button
              onClick={() => handleDelete(template)}
              className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
            >
              Eliminar
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
