import React from 'react';
import { useTemplateStore } from '../store/templateStore';
import PlantillasList from './PlantillasList';
import type { Plantilla } from '../types';

const PlantillasManager: React.FC = () => {
  const { templates, deleteTemplate, updateTemplate } = useTemplateStore();

  const handleEdit = (id: string) => {
    // Implementar la lógica de edición usando el store
    console.log('Edit template:', id);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTemplate(id);
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  return (
    <div className="container mx-auto px-4">
      <PlantillasList
        plantillas={templates}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default PlantillasManager;
