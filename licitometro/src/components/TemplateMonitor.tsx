import React, { useState, useEffect } from 'react';
import { useTemplateStore } from '../../store/templateStore';
import { TemplateService } from '../../services/templateService';
import type { ScrapingTemplate } from '../../types/recon';

interface RunHistory {
  id: string;
  startedAt: Date;
  finishedAt: Date;
  status: 'success' | 'error' | 'partial';
  itemsProcessed: number;
  error?: string;
}

interface TemplateMonitorProps {
  template: ScrapingTemplate;
}

export const TemplateMonitor: React.FC<TemplateMonitorProps> = ({ template }) => {
  const [history, setHistory] = useState<RunHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runningJob, setRunningJob] = useState<{
    jobId: string;
    status: 'queued' | 'running' | 'completed' | 'failed';
  } | null>(null);

  useEffect(() => {
    loadHistory();
  }, [template.id]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await TemplateService.getTemplateHistory(template.id);
      setHistory(data.runs);
      setError(null);
    } catch (err) {
      console.error('Error loading template history:', err);
      setError('Error al cargar el historial de ejecuciones');
    } finally {
      setLoading(false);
    }
  };

  const handleRunTemplate = async () => {
    try {
      setLoading(true);
      setError(null);
      const job = await TemplateService.runTemplate(template.id);
      setRunningJob(job);
      // Iniciar polling del estado del job
      pollJobStatus(job.jobId);
    } catch (err) {
      console.error('Error running template:', err);
      setError('Error al ejecutar la plantilla');
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await TemplateService.getTemplateHistory(template.id);
        const currentJob = status.runs.find(run => run.id === jobId);
        
        if (currentJob) {
          if (currentJob.status !== 'running' && currentJob.status !== 'queued') {
            clearInterval(interval);
            setRunningJob(null);
            loadHistory(); // Recargar historial completo
          }
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        clearInterval(interval);
        setRunningJob(null);
      }
    }, 5000); // Polling cada 5 segundos

    // Limpiar intervalo cuando el componente se desmonte
    return () => clearInterval(interval);
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'partial':
        return 'bg-yellow-100 text-yellow-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && !history.length) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

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
          Monitor de Ejecución
        </h3>
        <button
          onClick={handleRunTemplate}
          disabled={loading || !!runningJob}
          className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
            loading || runningJob
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
              Procesando...
            </>
          ) : runningJob ? (
            'Ejecutando...'
          ) : (
            'Ejecutar Ahora'
          )}
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" className="divide-y divide-gray-200">
          {history.map((run) => (
            <li key={run.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(
                          run.status
                        )}`}
                      >
                        {run.status === 'success'
                          ? 'Exitoso'
                          : run.status === 'error'
                          ? 'Error'
                          : run.status === 'partial'
                          ? 'Parcial'
                          : 'En Proceso'}
                      </span>
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {new Date(run.startedAt).toLocaleString()}
                      </p>
                    </div>
                    {run.error && (
                      <p className="mt-1 text-sm text-red-600">{run.error}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="flex items-center text-sm text-gray-500">
                      <svg
                        className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {run.itemsProcessed} items procesados
                    </span>
                    <span className="text-sm text-gray-500">
                      {((new Date(run.finishedAt).getTime() -
                        new Date(run.startedAt).getTime()) /
                        1000).toFixed(1)}s
                    </span>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
