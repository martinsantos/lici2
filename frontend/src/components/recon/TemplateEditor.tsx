import React, { useState } from 'react';
import type { Template, Field } from '../../types/recon';

export const TemplateEditor: React.FC = () => {
  const [template, setTemplate] = useState<Template>({
    name: '',
    description: '',
    sourceFields: [],
    destinationFields: [],
    mappings: []
  });

  const handleAddSourceField = () => {
    setTemplate(prev => ({
      ...prev,
      sourceFields: [...prev.sourceFields, { id: Date.now().toString(), name: '', selector: '', type: 'text' }]
    }));
  };

  const handleAddDestinationField = () => {
    setTemplate(prev => ({
      ...prev,
      destinationFields: [...prev.destinationFields, { id: Date.now().toString(), name: '', type: 'text' }]
    }));
  };

  const handleFieldDrop = (sourceId: string, destinationId: string) => {
    setTemplate(prev => ({
      ...prev,
      mappings: [...prev.mappings, { sourceId, destinationId }]
    }));
  };

  return (
    <div className="grid grid-cols-2 gap-8">
      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Campos de Origen</h3>
        <div className="space-y-4">
          {template.sourceFields.map(field => (
            <div key={field.id} className="flex items-center space-x-4">
              <input
                type="text"
                placeholder="Nombre del campo"
                className="border rounded px-3 py-2 w-full"
                value={field.name}
                onChange={(e) => {
                  const updatedFields = template.sourceFields.map(f =>
                    f.id === field.id ? { ...f, name: e.target.value } : f
                  );
                  setTemplate(prev => ({ ...prev, sourceFields: updatedFields }));
                }}
              />
              <input
                type="text"
                placeholder="Selector CSS"
                className="border rounded px-3 py-2 w-full"
                value={field.selector}
                onChange={(e) => {
                  const updatedFields = template.sourceFields.map(f =>
                    f.id === field.id ? { ...f, selector: e.target.value } : f
                  );
                  setTemplate(prev => ({ ...prev, sourceFields: updatedFields }));
                }}
              />
            </div>
          ))}
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            onClick={handleAddSourceField}
          >
            Agregar Campo de Origen
          </button>
        </div>
      </div>

      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Campos de Destino</h3>
        <div className="space-y-4">
          {template.destinationFields.map(field => (
            <div key={field.id} className="flex items-center space-x-4">
              <input
                type="text"
                placeholder="Nombre del campo"
                className="border rounded px-3 py-2 w-full"
                value={field.name}
                onChange={(e) => {
                  const updatedFields = template.destinationFields.map(f =>
                    f.id === field.id ? { ...f, name: e.target.value } : f
                  );
                  setTemplate(prev => ({ ...prev, destinationFields: updatedFields }));
                }}
              />
            </div>
          ))}
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            onClick={handleAddDestinationField}
          >
            Agregar Campo de Destino
          </button>
        </div>
      </div>

      <div className="col-span-2 border rounded-lg p-4 mt-8">
        <h3 className="text-lg font-semibold mb-4">Mapeo de Campos</h3>
        <div className="grid grid-cols-3 gap-4">
          {template.mappings.map((mapping, index) => {
            const sourceField = template.sourceFields.find(f => f.id === mapping.sourceId);
            const destField = template.destinationFields.find(f => f.id === mapping.destinationId);
            return (
              <div key={index} className="flex items-center space-x-2">
                <span>{sourceField?.name}</span>
                <span>→</span>
                <span>{destField?.name}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
