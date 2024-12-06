import * as React from 'react';
import { useState, useEffect, useCallback } from 'react';
import { useAppContext } from '../store/AppContext';
import { useNotification } from '../store/NotificationContext';
import toast from 'react-hot-toast';
import { FaUpload, FaTrash, FaFile } from 'react-icons/fa';

// Helper functions
const getFileName = (doc: any): string => {
  if (!doc) return 'Documento';
  if (typeof doc === 'string') {
    try {
      const parts = doc.split('/');
      return parts[parts.length - 1].replace(/^\d+-/, '') || 'Documento';
    } catch (e) {
      console.error('Error parsing filename:', e);
      return 'Documento';
    }
  }
  return doc.nombre || doc.filename || doc.originalName || 'Documento';
};

const getFileUrl = (doc: any): string => {
  if (!doc) return '';
  if (typeof doc === 'string') return doc;
  
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  if (doc.url) {
    if (doc.url.startsWith('http')) {
      return doc.url;
    }
    return `${baseUrl}${doc.url}`;
  }
  
  if (doc.id) {
    return `${baseUrl}/api/documents/download/${doc.id}`;
  }
  
  return '';
};

const formatDateForInput = (date: string | Date | null | undefined): string => {
  if (!date) return '';
  
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    return d.toISOString().split('T')[0];
  } catch (e) {
    console.error('Error formatting date:', e);
    return '';
  }
};

const formatDateForAPI = (date: string | Date | null | undefined): string => {
  const formattedDate = formatDateForInput(date);
  return formattedDate ? `${formattedDate}T00:00:00` : '';
};

interface LicitacionFormProps {
  onSuccess?: () => void;
  initialData?: any;
  isEditing?: boolean;
}

const defaultFormData = {
  titulo: '',
  descripcion: '',
  presupuesto: '',
  fecha_inicio: '',
  fecha_fin: '',
  estado: 'pendiente',
  documentos: [],
  monto: '',
  moneda: 'ARS',
  idioma: 'es',
  categoria: '',
  ubicacion: '',
  plazo: '',
  etapa: '',
  modalidad: '',
  area: '',
  requisitos: [],
  garantia: {}
};

function LicitacionForm({ onSuccess, initialData, isEditing = false }: LicitacionFormProps) {
  const { state, dispatch } = useAppContext();
  const { showNotification } = useNotification();
  
  const [formData, setFormData] = useState(defaultFormData);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [documentos, setDocumentos] = useState<File[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...initialData,
        presupuesto: initialData.presupuesto?.toString() || '',
        fecha_inicio: formatDateForInput(initialData.fecha_inicio),
        fecha_fin: formatDateForInput(initialData.fecha_fin),
      });
    }
  }, [initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const formDataToSend = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        if (key !== 'documentos' && value !== null && value !== undefined) {
          formDataToSend.append(key, value.toString());
        }
      });

      documentos.forEach((doc) => {
        formDataToSend.append('documentos', doc);
      });

      const baseUrl = import.meta.env.PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const url = isEditing ? 
        `${baseUrl}/api/licitaciones/${initialData.id}` : 
        `${baseUrl}/api/licitaciones`;

      const response = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        },
        body: formDataToSend,
      });

      if (!response.ok) {
        const errorData = await response.text();
        console.error('Server error:', errorData);
        throw new Error(`Error ${isEditing ? 'actualizando' : 'creando'} la licitación: ${errorData}`);
      }

      const result = await response.json();
      toast.success(`Licitación ${isEditing ? 'actualizada' : 'creada'} exitosamente`);
      
      if (onSuccess) {
        onSuccess();
      }

      // Navigate using window.location after successful submission
      window.location.href = `/licitaciones/${isEditing ? initialData.id : result.id}`;
    } catch (error) {
      console.error('Error:', error);
      toast.error(error instanceof Error ? error.message : 'Error al procesar la solicitud');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setDocumentos(prev => [...prev, ...Array.from(e.target.files || [])]);
    }
  };

  const removeDocument = (index: number) => {
    setDocumentos(prev => prev.filter((_, i) => i !== index));
  };

  const removeExistingDocument = async (docId: number) => {
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/documentos/${docId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Error al eliminar el documento');
      }

      setFormData(prev => ({
        ...prev,
        documentos: prev.documentos.filter((doc: any) => doc.id !== docId)
      }));

      toast.success('Documento eliminado exitosamente');
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error al eliminar el documento');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
      {isSubmitting && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Guardando...</h3>
            </div>
          </div>
        </div>
      )}

      <div>
        <label htmlFor="titulo" className="block text-sm font-medium text-gray-700">
          Título
        </label>
        <input
          type="text"
          id="titulo"
          name="titulo"
          value={formData.titulo}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">
          Descripción
        </label>
        <textarea
          id="descripcion"
          name="descripcion"
          value={formData.descripcion}
          onChange={handleInputChange}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label htmlFor="presupuesto" className="block text-sm font-medium text-gray-700">
          Presupuesto
        </label>
        <input
          type="number"
          id="presupuesto"
          name="presupuesto"
          value={formData.presupuesto}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label htmlFor="fecha_inicio" className="block text-sm font-medium text-gray-700">
          Fecha de Inicio
        </label>
        <input
          type="date"
          id="fecha_inicio"
          name="fecha_inicio"
          value={formData.fecha_inicio}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label htmlFor="fecha_fin" className="block text-sm font-medium text-gray-700">
          Fecha de Fin
        </label>
        <input
          type="date"
          id="fecha_fin"
          name="fecha_fin"
          value={formData.fecha_fin}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label htmlFor="estado" className="block text-sm font-medium text-gray-700">
          Estado
        </label>
        <select
          id="estado"
          name="estado"
          value={formData.estado}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        >
          <option value="pendiente">Pendiente</option>
          <option value="en_proceso">En Proceso</option>
          <option value="finalizada">Finalizada</option>
          <option value="cancelada">Cancelada</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Documentos
        </label>
        
        {/* Existing documents */}
        {isEditing && formData.documentos && formData.documentos.length > 0 && (
          <div className="mt-2 space-y-2">
            {formData.documentos.map((doc: any, index: number) => (
              <div key={doc.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                <div className="flex items-center">
                  <FaFile className="text-gray-400 mr-2" />
                  <a
                    href={getFileUrl(doc)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-indigo-600 hover:text-indigo-900"
                  >
                    {getFileName(doc)}
                  </a>
                </div>
                <button
                  type="button"
                  onClick={() => removeExistingDocument(doc.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  <FaTrash className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* New documents */}
        <div className="mt-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            multiple
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FaUpload className="mr-2" />
            Subir Documentos
          </button>
        </div>

        {documentos.length > 0 && (
          <div className="mt-2 space-y-2">
            {documentos.map((doc, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                <div className="flex items-center">
                  <FaFile className="text-gray-400 mr-2" />
                  <span className="text-sm text-gray-900">{doc.name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeDocument(index)}
                  className="text-red-600 hover:text-red-900"
                >
                  <FaTrash className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-end space-x-3 pt-6">
        {isEditing && (
          <a
            href={`/licitaciones/${initialData.id}`}
            className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Cancelar
          </a>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isSubmitting ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear'}
        </button>
      </div>
    </form>
  );
}

export default LicitacionForm;
