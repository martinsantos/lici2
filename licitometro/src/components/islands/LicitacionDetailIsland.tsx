import React, { useState } from 'react';
import type { Licitacion } from '../../types';
import DocumentList from '../DocumentList';

interface LicitacionDetailIslandProps {
  licitacion: Licitacion;
  client: boolean;
}

export default function LicitacionDetailIsland({ licitacion, client = false }: LicitacionDetailIslandProps) {
  const [isParticipating, setIsParticipating] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  if (!client) {
    return <div className="animate-pulse bg-gray-200 h-96 rounded-md"></div>;
  }

  const handleParticipate = () => {
    setShowConfirmation(true);
  };

  const confirmParticipation = async () => {
    try {
      // Aquí iría la lógica para confirmar la participación
      setIsParticipating(true);
      setShowConfirmation(false);
    } catch (error) {
      console.error('Error al confirmar participación:', error);
    }
  };

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <div className="mb-8">
        <div className="flex justify-between items-start">
          <h1 className="text-2xl font-bold text-gray-900">{licitacion.titulo}</h1>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            licitacion.estado === 'Abierta' ? 'bg-green-100 text-green-800' :
            licitacion.estado === 'Cerrada' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {licitacion.estado}
          </span>
        </div>
        <p className="mt-4 text-gray-600">{licitacion.descripcion}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Detalles de la Licitación</h2>
          <dl className="grid grid-cols-1 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Organismo</dt>
              <dd className="mt-1 text-sm text-gray-900">{licitacion.organismo}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Presupuesto</dt>
              <dd className="mt-1 text-sm text-gray-900">${licitacion.presupuesto.toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Fecha de Apertura</dt>
              <dd className="mt-1 text-sm text-gray-900">{new Date(licitacion.fechaApertura).toLocaleDateString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Fecha de Cierre</dt>
              <dd className="mt-1 text-sm text-gray-900">{new Date(licitacion.fechaCierre).toLocaleDateString()}</dd>
            </div>
          </dl>
        </div>

        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Documentos</h2>
          <DocumentList documentos={licitacion.documentos || []} />
        </div>
      </div>

      <div className="border-t pt-6">
        {!isParticipating ? (
          <button
            onClick={handleParticipate}
            className="w-full md:w-auto px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Participar en esta Licitación
          </button>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Ya estás participando en esta licitación
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showConfirmation && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Confirmar Participación
            </h3>
            <p className="text-sm text-gray-500 mb-6">
              ¿Estás seguro que deseas participar en esta licitación? Una vez confirmada tu participación, recibirás todas las actualizaciones y notificaciones relacionadas.
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowConfirmation(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                onClick={confirmParticipation}
                className="px-4 py-2 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
