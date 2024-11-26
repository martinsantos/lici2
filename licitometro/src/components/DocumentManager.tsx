import React, { useState } from 'react';
import { formatFileSize } from '../utils/formatters';

interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadDate: string;
}

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      // Aquí iría la lógica de carga del archivo
      const newDoc: Document = {
        id: Date.now().toString(),
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        uploadDate: new Date().toISOString()
      };

      setDocuments([...documents, newDoc]);
      setSelectedFile(null);
    } catch (error) {
      console.error('Error uploading document:', error);
    }
  };

  return (
    <div className="p-4">
      <div className="mb-4">
        <input
          type="file"
          onChange={handleFileSelect}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
        {selectedFile && (
          <div className="mt-2">
            <p className="text-sm text-gray-600">
              Archivo seleccionado: {selectedFile.name} ({formatFileSize(selectedFile.size)})
            </p>
            <button
              onClick={handleUpload}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Subir Documento
            </button>
          </div>
        )}
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Documentos Subidos</h3>
        {documents.length === 0 ? (
          <p className="text-gray-500">No hay documentos subidos</p>
        ) : (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li key={doc.id} className="flex items-center justify-between p-3 bg-white rounded-lg shadow">
                <div>
                  <p className="font-medium">{doc.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(doc.size)} • {new Date(doc.uploadDate).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setDocuments(documents.filter(d => d.id !== doc.id));
                  }}
                  className="text-red-600 hover:text-red-800"
                >
                  Eliminar
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default DocumentManager;
