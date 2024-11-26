import React, { useState, useEffect } from 'react';
import { DocumentService } from '../services/documentService';

interface DocumentViewerProps {
  documentId: string;
  onClose?: () => void;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ documentId, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [documento, setDocumento] = useState<{ url: string; tipo: string; nombre: string } | null>(null);

  useEffect(() => {
    const loadDocument = async () => {
      try {
        setLoading(true);
        setError(null);
        const doc = await DocumentService.getDocumento(documentId);
        setDocumento({
          url: doc.url,
          tipo: doc.tipo,
          nombre: doc.nombre
        });
      } catch (err) {
        setError('Error al cargar el documento');
        console.error('Error loading document:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDocument();
  }, [documentId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !documento) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-red-600">Error</h3>
        <p className="mt-2 text-sm text-gray-500">{error || 'No se pudo cargar el documento'}</p>
        {onClose && (
          <button
            onClick={onClose}
            className="mt-4 inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
          >
            Cerrar
          </button>
        )}
      </div>
    );
  }

  const ViewerContent = () => {
    switch (documento.tipo) {
      case 'pdf':
        return (
          <iframe
            src={documento.url}
            title={documento.nombre}
            className="w-full h-full rounded-lg shadow-lg"
            style={{ minHeight: '600px' }}
          />
        );
      case 'doc':
      case 'docx':
      case 'xls':
      case 'xlsx':
      case 'ppt':
      case 'pptx':
        return (
          <iframe
            src={`https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(documento.url)}`}
            title={documento.nombre}
            className="w-full h-full rounded-lg shadow-lg"
            style={{ minHeight: '600px' }}
          />
        );
      default:
        return (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900">
              Vista previa no disponible para {documento.nombre}
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              Este tipo de archivo no puede ser visualizado directamente.
            </p>
            <div className="mt-4 space-x-4">
              <a
                href={documento.url}
                download={documento.nombre}
                className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
              >
                Descargar
              </a>
              {onClose && (
                <button
                  onClick={onClose}
                  className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  Cerrar
                </button>
              )}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="relative bg-white p-4 rounded-xl shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">{documento.nombre}</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-md bg-white p-2 text-gray-400 hover:text-gray-500"
          >
            <span className="sr-only">Cerrar</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      <ViewerContent />
    </div>
  );
};

export default DocumentViewer;
