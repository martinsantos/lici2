import React, { useState } from 'react';
import type { Documento } from '../types';
import { DocumentService } from '../services/documentService';

interface DocumentDownloadButtonProps {
  documento: Documento;
}

export default function DocumentDownloadButton({ documento }: DocumentDownloadButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    setIsLoading(true);
    setError(null);

    try {
      await DocumentService.downloadDocument(documento);
    } catch (error) {
      console.error('Error al descargar el archivo:', error);
      setError(error instanceof Error ? error.message : 'Error al descargar el archivo');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col">
      <button
        onClick={handleDownload}
        disabled={isLoading}
        type="button"
        className={`flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 ${
          isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        }`}
      >
        <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
            clipRule="evenodd"
          />
        </svg>
        <span>{isLoading ? 'Descargando...' : documento.nombre}</span>
      </button>
      {error && (
        <p className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
