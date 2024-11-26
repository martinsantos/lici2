import React from 'react';
import type { Licitacion } from '../types';
import LicitacionCard from './LicitacionCard';

interface LicitacionesListProps {
  licitaciones: Licitacion[];
  isLoading?: boolean;
}

const LoadingSkeleton = () => (
  <div className="animate-pulse">
    <div className="bg-gray-200 h-40 rounded-lg mb-4"></div>
    <div className="bg-gray-200 h-40 rounded-lg mb-4"></div>
    <div className="bg-gray-200 h-40 rounded-lg"></div>
  </div>
);

const LicitacionesList: React.FC<LicitacionesListProps> = ({ licitaciones, isLoading = false }) => {
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (licitaciones.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">No se encontraron licitaciones</h3>
        <p className="mt-2 text-sm text-gray-500">
          Intenta ajustar los filtros de búsqueda o prueba con otros términos.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {licitaciones.map((licitacion) => (
        <LicitacionCard key={licitacion.id} licitacion={licitacion} />
      ))}
    </div>
  );
};

export default LicitacionesList;
