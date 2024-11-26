import React, { useState } from 'react';
import { TemplateService } from '../../services/templateService';
import type { ScrapingTemplate } from '../../types/recon';

interface TemplatePreviewProps {
  template: ScrapingTemplate;
}

export const TemplatePreview: React.FC<TemplatePreviewProps> = ({ template }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);

  const handleTestTemplate = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await TemplateService.testTemplate(template.id);
      
      if (result.success) {
        setPreviewData(result.data);
      } else {
        setError(result.error || 'Error al obtener la vista previa');
      }
    } catch (err) {
      console.error('Error testing template:', err);
      setError('Error al probar la plantilla');
    } finally {
      setLoading(false);
    }
  };

  const renderPreviewContent = () => {
    if (!previewData) return null;

    return (
      <div className="mt-4 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flow-root">
            <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead>
                    <tr>
                      {template.fields.map((field) => (
                        <th
                          key={field.id}
                          scope="col"
                          className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900"
                        >
                          {field.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {Array.isArray(previewData) ? (
                      previewData.map((item, index) => (
                        <tr key={index}>
                          {template.fields.map((field) => (
                            <td
                              key={field.id}
                              className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-500"
                            >
                              {item[field.name]}
                            </td>
                          ))}
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td
                          colSpan={template.fields.length}
                          className="px-4 py-4 text-sm text-gray-500"
                        >
                          No se encontraron resultados
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">{error}</h3>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Vista Previa de Resultados
        </h3>
        <button
          onClick={handleTestTemplate}
          disabled={loading}
          className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700'
          }`}
        >
          {loading ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Obteniendo vista previa...
            </>
          ) : (
            'Probar Plantilla'
          )}
        </button>
      </div>

      {renderPreviewContent()}
    </div>
  );
};
