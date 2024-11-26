import React from 'react';
import type { Plantilla } from '../types';

interface PlantillaCardProps {
  plantilla: Plantilla;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

const PlantillaCard: React.FC<PlantillaCardProps> = ({ plantilla, onEdit, onDelete }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{plantilla.nombre}</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(plantilla.id)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Editar
          </button>
          <button
            onClick={() => onDelete(plantilla.id)}
            className="text-red-600 hover:text-red-700 text-sm font-medium"
          >
            Eliminar
          </button>
        </div>
      </div>
      <p className="text-gray-600 text-sm mb-4">{plantilla.descripcion}</p>
      <div className="flex flex-wrap gap-2 mt-4">
        {plantilla.campos.map((campo) => (
          <span
            key={campo.id}
            className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded"
          >
            {campo.nombre}
          </span>
        ))}
      </div>
    </div>
  );
};

export default PlantillaCard;
