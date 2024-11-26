import React, { useState } from 'react';
import { useTemplateStore } from '../store/templateStore';
import type { ScrapingTemplate, TemplateField } from '../types/recon';

interface TemplateEditorProps {
  onClose: () => void;
}

export const TemplateEditor: React.FC<TemplateEditorProps> = ({ onClose }) => {
  const { selectedTemplate, addTemplate, updateTemplate } = useTemplateStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<Partial<ScrapingTemplate>>({
    name: selectedTemplate?.name || '',
    description: selectedTemplate?.description || '',
    url: selectedTemplate?.url || '',
    fields: selectedTemplate?.fields || []
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (selectedTemplate) {
        await updateTemplate(selectedTemplate.id, formData as ScrapingTemplate);
      } else {
        await addTemplate(formData as ScrapingTemplate);
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar la plantilla');
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (index: number, field: Partial<TemplateField>) => {
    const newFields = [...(formData.fields || [])];
    newFields[index] = { ...newFields[index], ...field };
    setFormData({ ...formData, fields: newFields });
  };

  const addField = () => {
    const newField: TemplateField = {
      id: `field-${Date.now()}`,
      name: '',
      selector: '',
      type: 'text',
      required: false
    };
    setFormData({
      ...formData,
      fields: [...(formData.fields || []), newField]
    });
  };

  const removeField = (index: number) => {
    const newFields = formData.fields?.filter((_, i) => i !== index);
    setFormData({ ...formData, fields: newFields });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {selectedTemplate ? 'Editar Plantilla' : 'Nueva Plantilla'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nombre</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Descripción</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">URL</label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">Campos</label>
              <button
                type="button"
                onClick={addField}
                className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Agregar Campo
              </button>
            </div>
            
            <div className="space-y-4">
              {formData.fields?.map((field, index) => (
                <div key={field.id} className="border rounded-lg p-4 relative">
                  <button
                    type="button"
                    onClick={() => removeField(index)}
                    className="absolute top-2 right-2 text-red-600 hover:text-red-800"
                  >
                    ×
                  </button>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Nombre del Campo</label>
                      <input
                        type="text"
                        value={field.name}
                        onChange={(e) => handleFieldChange(index, { name: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Selector</label>
                      <input
                        type="text"
                        value={field.selector}
                        onChange={(e) => handleFieldChange(index, { selector: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Tipo</label>
                      <select
                        value={field.type}
                        onChange={(e) => handleFieldChange(index, { type: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      >
                        <option value="text">Texto</option>
                        <option value="number">Número</option>
                        <option value="date">Fecha</option>
                        <option value="link">Enlace</option>
                        <option value="image">Imagen</option>
                      </select>
                    </div>
                    
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={field.required}
                        onChange={(e) => handleFieldChange(index, { required: e.target.checked })}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 block text-sm text-gray-900">
                        Requerido
                      </label>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
