import React, { useState } from 'react';
import type { Plantilla, Campo } from '../types';

interface PlantillaEditorProps {
  plantilla?: Plantilla;
  onSave: (plantilla: Plantilla) => void;
  onCancel: () => void;
}

const initialCampo: Campo = {
  id: '',
  nombre: '',
  tipo: 'texto',
  requerido: false,
};

const PlantillaEditor: React.FC<PlantillaEditorProps> = ({ plantilla, onSave, onCancel }) => {
  const [nombre, setNombre] = useState(plantilla?.nombre || '');
  const [descripcion, setDescripcion] = useState(plantilla?.descripcion || '');
  const [campos, setCampos] = useState<Campo[]>(plantilla?.campos || [initialCampo]);

  const handleCampoChange = (index: number, campo: Partial<Campo>) => {
    const newCampos = [...campos];
    newCampos[index] = { ...newCampos[index], ...campo };
    setCampos(newCampos);
  };

  const addCampo = () => {
    setCampos([...campos, initialCampo]);
  };

  const removeCampo = (index: number) => {
    setCampos(campos.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newPlantilla: Plantilla = {
      id: plantilla?.id || Date.now().toString(),
      nombre,
      descripcion,
      campos,
      fuente: plantilla?.fuente || 'manual',
      activa: plantilla?.activa || true,
    };
    onSave(newPlantilla);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">
          Nombre de la Plantilla
        </label>
        <input
          type="text"
          id="nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          required
        />
      </div>

      <div>
        <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">
          Descripción
        </label>
        <textarea
          id="descripcion"
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        />
      </div>

      <div>
        <h4 className="text-lg font-medium text-gray-900">Campos</h4>
        {campos.map((campo, index) => (
          <div key={index} className="mt-4 border-t border-gray-200 pt-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <label htmlFor={`campo-nombre-${index}`} className="block text-sm font-medium text-gray-700">
                  Nombre del Campo
                </label>
                <input
                  type="text"
                  id={`campo-nombre-${index}`}
                  value={campo.nombre}
                  onChange={(e) => handleCampoChange(index, { nombre: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  required
                />
              </div>
              <div className="flex-1">
                <label htmlFor={`campo-tipo-${index}`} className="block text-sm font-medium text-gray-700">
                  Tipo
                </label>
                <select
                  id={`campo-tipo-${index}`}
                  value={campo.tipo}
                  onChange={(e) => handleCampoChange(index, { tipo: e.target.value as Campo['tipo'] })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="texto">Texto</option>
                  <option value="numero">Número</option>
                  <option value="fecha">Fecha</option>
                  <option value="lista">Lista</option>
                  <option value="booleano">Booleano</option>
                </select>
              </div>
              <div className="flex items-center">
                <label htmlFor={`campo-requerido-${index}`} className="block text-sm font-medium text-gray-700">
                  Requerido
                </label>
                <input
                  type="checkbox"
                  id={`campo-requerido-${index}`}
                  checked={campo.requerido}
                  onChange={(e) => handleCampoChange(index, { requerido: e.target.checked })}
                  className="ml-2 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
              </div>
              <button
                type="button"
                onClick={() => removeCampo(index)}
                className="text-red-600 hover:text-red-700 text-sm font-medium"
              >
                Eliminar
              </button>
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={addCampo}
          className="mt-4 inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          Añadir Campo
        </button>
      </div>

      <div className="flex justify-end space-x-4">
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          Guardar
        </button>
      </div>
    </form>
  );
};

export default PlantillaEditor;
