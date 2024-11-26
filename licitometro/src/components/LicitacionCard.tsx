import React from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Licitacion } from '../types';

interface LicitacionCardProps {
  licitacion: Licitacion;
}

const estadoClasses = {
  abierta: 'bg-green-100 text-green-800',
  cerrada: 'bg-red-100 text-red-800',
  adjudicada: 'bg-blue-100 text-blue-800',
  desierta: 'bg-gray-100 text-gray-800',
};

const LicitacionCard: React.FC<LicitacionCardProps> = ({ licitacion }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(amount);
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{licitacion.titulo}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${estadoClasses[licitacion.estado]}`}>
          {licitacion.estado.charAt(0).toUpperCase() + licitacion.estado.slice(1)}
        </span>
      </div>
      
      <p className="text-gray-600 text-sm mb-4">{licitacion.descripcion}</p>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Entidad</p>
          <p className="text-sm font-medium">{licitacion.entidad}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Presupuesto</p>
          <p className="text-sm font-medium">{formatCurrency(licitacion.presupuesto)}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Fecha Publicación</p>
          <p className="text-sm font-medium">
            {format(new Date(licitacion.fechaPublicacion), 'dd MMM yyyy', { locale: es })}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Fecha Cierre</p>
          <p className="text-sm font-medium">
            {format(new Date(licitacion.fechaCierre), 'dd MMM yyyy', { locale: es })}
          </p>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 mt-4">
        {licitacion.tags.map((tag) => (
          <span
            key={tag}
            className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded"
          >
            {tag}
          </span>
        ))}
      </div>
      
      <div className="mt-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            {licitacion.documentos.length} documento(s)
          </span>
        </div>
        <a
          href={`/licitaciones/${licitacion.id}`}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          Ver detalles →
        </a>
      </div>
    </div>
  );
};

export default LicitacionCard;
