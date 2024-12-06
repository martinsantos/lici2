import React from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { FaFileAlt, FaCalendarAlt, FaBuilding, FaMoneyBillWave, FaClock, FaDownload, FaExternalLinkAlt } from 'react-icons/fa';
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
        <div className="flex items-center">
          <FaBuilding className="text-gray-400 mr-2" />
          <div>
            <p className="text-sm text-gray-500">Entidad</p>
            <p className="text-sm font-medium">{licitacion.entidad}</p>
          </div>
        </div>
        <div className="flex items-center">
          <FaMoneyBillWave className="text-gray-400 mr-2" />
          <div>
            <p className="text-sm text-gray-500">Presupuesto</p>
            <p className="text-sm font-medium">{formatCurrency(licitacion.presupuesto)}</p>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center">
          <FaCalendarAlt className="text-gray-400 mr-2" />
          <div>
            <p className="text-sm text-gray-500">Fecha Publicación</p>
            <p className="text-sm font-medium">
              {format(new Date(licitacion.fechaPublicacion), 'dd MMM yyyy', { locale: es })}
            </p>
          </div>
        </div>
        <div className="flex items-center">
          <FaClock className="text-gray-400 mr-2" />
          <div>
            <p className="text-sm text-gray-500">Fecha Cierre</p>
            <p className="text-sm font-medium">
              {format(new Date(licitacion.fechaCierre), 'dd MMM yyyy', { locale: es })}
            </p>
          </div>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 mt-4">
        {licitacion.tags?.map((tag) => (
          <span
            key={tag}
            className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded"
          >
            {tag}
          </span>
        ))}
      </div>
      
      <div className="mt-4">
        <div className="flex items-center mb-2">
          <FaFileAlt className="text-gray-400 mr-2" />
          <p className="text-sm text-gray-500">Documentos ({licitacion.documentos?.length || 0})</p>
        </div>
        {licitacion.documentos && licitacion.documentos.length > 0 ? (
          <div className="space-y-2">
            {licitacion.documentos.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between bg-gray-50 p-2 rounded hover:bg-gray-100 transition-colors">
                <div className="flex items-center">
                  <FaFileAlt className="text-gray-400 mr-2" />
                  <span className="text-sm truncate max-w-xs">{doc.nombre}</span>
                </div>
                <div className="flex space-x-2">
                  <a
                    href={doc.url}
                    className="text-primary-600 hover:text-primary-700 p-1 rounded hover:bg-gray-200 transition-colors"
                    title="Descargar documento"
                    download
                  >
                    <FaDownload className="w-4 h-4" />
                  </a>
                  <a
                    href={doc.url}
                    className="text-primary-600 hover:text-primary-700 p-1 rounded hover:bg-gray-200 transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                    title="Ver documento"
                  >
                    <FaExternalLinkAlt className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 italic">No hay documentos disponibles</p>
        )}
      </div>
      
      <div className="mt-6 flex justify-end">
        <a
          href={`/licitaciones/${licitacion.id}`}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Ver detalles <FaExternalLinkAlt className="ml-2 w-4 h-4" />
        </a>
      </div>
    </div>
  );
};

export default LicitacionCard;
