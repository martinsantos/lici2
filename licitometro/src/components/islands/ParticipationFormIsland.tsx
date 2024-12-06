import React, { useState } from 'react';
import type { Licitacion } from '../../types';

interface ParticipationFormIslandProps {
  licitacion: Licitacion;
  client: boolean;
  onSubmit: (data: any) => void;
}

export default function ParticipationFormIsland({ licitacion, client = false, onSubmit }: ParticipationFormIslandProps) {
  const [formData, setFormData] = useState({
    nombreEmpresa: '',
    rut: '',
    representanteLegal: '',
    email: '',
    telefono: '',
    documentos: [] as File[],
    comentarios: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  if (!client) {
    return <div className="animate-pulse bg-gray-200 h-96 rounded-md"></div>;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData(prev => ({
        ...prev,
        documentos: Array.from(e.target.files || [])
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError('');

    try {
      await onSubmit(formData);
      // Resetear el formulario después del envío exitoso
      setFormData({
        nombreEmpresa: '',
        rut: '',
        representanteLegal: '',
        email: '',
        telefono: '',
        documentos: [],
        comentarios: ''
      });
    } catch (error) {
      setSubmitError('Error al enviar el formulario. Por favor, intente nuevamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white shadow-sm rounded-lg p-6">
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Formulario de Participación - {licitacion.titulo}
        </h2>
        <p className="text-sm text-gray-500 mb-6">
          Complete los siguientes datos para participar en esta licitación.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor="nombreEmpresa" className="block text-sm font-medium text-gray-700">
            Nombre de la Empresa
          </label>
          <input
            type="text"
            name="nombreEmpresa"
            id="nombreEmpresa"
            required
            value={formData.nombreEmpresa}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="rut" className="block text-sm font-medium text-gray-700">
            RUT
          </label>
          <input
            type="text"
            name="rut"
            id="rut"
            required
            value={formData.rut}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="representanteLegal" className="block text-sm font-medium text-gray-700">
            Representante Legal
          </label>
          <input
            type="text"
            name="representanteLegal"
            id="representanteLegal"
            required
            value={formData.representanteLegal}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            name="email"
            id="email"
            required
            value={formData.email}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="telefono" className="block text-sm font-medium text-gray-700">
            Teléfono
          </label>
          <input
            type="tel"
            name="telefono"
            id="telefono"
            required
            value={formData.telefono}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="documentos" className="block text-sm font-medium text-gray-700">
            Documentos Requeridos
          </label>
          <input
            type="file"
            name="documentos"
            id="documentos"
            multiple
            onChange={handleFileChange}
            className="mt-1 block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-medium
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>

        <div className="sm:col-span-2">
          <label htmlFor="comentarios" className="block text-sm font-medium text-gray-700">
            Comentarios Adicionales
          </label>
          <textarea
            name="comentarios"
            id="comentarios"
            rows={4}
            value={formData.comentarios}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
      </div>

      {submitError && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{submitError}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className={`inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
            isSubmitting ? 'opacity-75 cursor-not-allowed' : ''
          }`}
        >
          {isSubmitting ? 'Enviando...' : 'Enviar Participación'}
        </button>
      </div>
    </form>
  );
}
