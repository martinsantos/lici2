import React, { useState, useEffect } from 'react';
import { ScrapingService } from '../../services/scrapingService';
import { Template, ScrapingResult } from '../../types/recon';
import { useToast } from '../../hooks/useToast';

interface ScrapingRunnerProps {
  template: Template;
  onComplete?: (result: ScrapingResult) => void;
}

export const ScrapingRunner: React.FC<ScrapingRunnerProps> = ({ template, onComplete }) => {
  const [url, setUrl] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'pending' | 'processing' | 'completed' | 'failed'>('idle');
  const [progress, setProgress] = useState<number>(0);
  const scrapingService = ScrapingService.getInstance();
  const toast = useToast();

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (jobId && (status === 'pending' || status === 'processing')) {
      intervalId = setInterval(async () => {
        try {
          const statusResponse = await scrapingService.getScrapingStatus(jobId);
          setStatus(statusResponse.status);
          if (statusResponse.progress) {
            setProgress(statusResponse.progress);
          }

          if (statusResponse.status === 'completed' && statusResponse.result) {
            clearInterval(intervalId);
            onComplete?.(statusResponse.result);
            toast.success('Scraping completado exitosamente');
          } else if (statusResponse.status === 'failed') {
            clearInterval(intervalId);
            toast.error('Error durante el scraping');
          }
        } catch (error) {
          console.error('Error checking scraping status:', error);
          toast.error('Error al verificar el estado del scraping');
        }
      }, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [jobId, status]);

  const handleStartScraping = async () => {
    if (!url) {
      toast.error('Por favor ingrese una URL');
      return;
    }

    try {
      setStatus('pending');
      const newJobId = await scrapingService.startScraping(template, url);
      setJobId(newJobId);
      toast.success('Scraping iniciado');
    } catch (error) {
      console.error('Error starting scraping:', error);
      setStatus('failed');
      toast.error('Error al iniciar el scraping');
    }
  };

  const handleCancel = async () => {
    if (jobId) {
      try {
        await scrapingService.cancelScraping(jobId);
        setStatus('idle');
        setJobId(null);
        setProgress(0);
        toast.info('Scraping cancelado');
      } catch (error) {
        console.error('Error canceling scraping:', error);
        toast.error('Error al cancelar el scraping');
      }
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Ingrese la URL a scrapear"
          className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={status !== 'idle'}
        />
        {status === 'idle' ? (
          <button
            onClick={handleStartScraping}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Iniciar Scraping
          </button>
        ) : (
          <button
            onClick={handleCancel}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Cancelar
          </button>
        )}
      </div>

      {(status === 'pending' || status === 'processing') && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progreso:</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-indigo-600 h-2.5 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600">
            {status === 'pending' ? 'Iniciando scraping...' : 'Procesando...'}
          </p>
        </div>
      )}
    </div>
  );
};
