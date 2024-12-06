import React, { useState } from 'react';
import type { Documento } from '../types';

interface DocumentLinkProps {
  documento: Documento;
}

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function DocumentLink({ documento }: DocumentLinkProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getDocumentUrl = (doc: Documento): string => {
    // Si es una URL completa, la usamos directamente
    if (doc.url.startsWith('http://') || doc.url.startsWith('https://')) {
      return doc.url;
    }
    
    // Si tenemos filePath, lo usamos para construir la URL
    if (doc.filePath) {
      return `${BACKEND_URL}/uploads/${doc.filePath}`;
    }
    
    // Si tenemos una URL relativa, la convertimos en absoluta
    const relativePath = doc.url.startsWith('/') ? doc.url.slice(1) : doc.url;
    return `${BACKEND_URL}/uploads/${relativePath}`;
  };

  const downloadFile = async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const url = getDocumentUrl(documento);
      console.log('Downloading from URL:', url); // Para debugging
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = documento.nombre;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(objectUrl);
    } catch (error) {
      console.error('Error downloading file:', error);
      setError(error instanceof Error ? error.message : 'Error al descargar el archivo');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col">
      <div className="flex items-center space-x-3">
        <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path 
            fillRule="evenodd" 
            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" 
            clipRule="evenodd" 
          />
        </svg>
        <button
          onClick={downloadFile}
          disabled={isLoading}
          className={`text-sm text-blue-600 hover:text-blue-800 cursor-pointer ${isLoading ? 'opacity-50' : ''}`}
        >
          {isLoading ? 'Descargando...' : documento.nombre}
        </button>
      </div>
      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}
