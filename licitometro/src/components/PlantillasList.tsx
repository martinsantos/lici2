import React from 'react';
import type { Plantilla } from '../types';
import PlantillaCard from './PlantillaCard';

interface PlantillasListProps {
  plantillas: Plantilla[];
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

const PlantillasList: React.FC<PlantillasListProps> = ({ plantillas, onEdit, onDelete }) => {
  if (plantillas.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">No se encontraron plantillas</h3>
        <p className="mt-2 text-sm text-gray-500">
          Intenta crear una nueva plantilla o ajustar los filtros de búsqueda.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {plantillas.map((plantilla) => (
        <PlantillaCard
          key={plantilla.id}
          plantilla={plantilla}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

export default PlantillasList;
