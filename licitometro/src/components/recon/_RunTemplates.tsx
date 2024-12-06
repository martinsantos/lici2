import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { ScrapingTemplate, TemplateRunResult } from '../../types/recon';
import { API_BASE_URL } from '../../config/api';

interface Props {
  templates: ScrapingTemplate[];
}

interface JobStatus {
  templateId: string;
  status: 'idle' | 'running' | 'completed' | 'error';
  progress?: number;
  error?: string;
  results?: TemplateRunResult[];
}

const RunTemplates: React.FC<Props> = ({ templates }) => {
  const [jobStatuses, setJobStatuses] = useState<Record<string, JobStatus>>({});
  const [selectedResults, setSelectedResults] = useState<TemplateRunResult[]>([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    // Inicializar estados de jobs
    const initialStatuses: Record<string, JobStatus> = {};
    templates.forEach((template) => {
      if (template.id) {
        initialStatuses[template.id] = {
          templateId: template.id,
          status: 'idle',
        };
      }
    });
    setJobStatuses(initialStatuses);
  }, [templates]);

  const startScraping = async (templateId: string) => {
    try {
      setJobStatuses((prev) => ({
        ...prev,
        [templateId]: { ...prev[templateId], status: 'running', progress: 0 },
      }));

      const response = await fetch(`${API_BASE_URL}/recon/start/${templateId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Iniciar polling del estado
      pollJobStatus(templateId);
    } catch (error) {
      console.error('Error starting scraping:', error);
      setJobStatuses((prev) => ({
        ...prev,
        [templateId]: {
          ...prev[templateId],
          status: 'error',
          error: 'Failed to start scraping',
        },
      }));
    }
  };

  const stopScraping = async (templateId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/recon/stop/${templateId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setJobStatuses((prev) => ({
        ...prev,
        [templateId]: { ...prev[templateId], status: 'idle' },
      }));
    } catch (error) {
      console.error('Error stopping scraping:', error);
    }
  };

  const pollJobStatus = async (templateId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/recon/status/${templateId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        setJobStatuses((prev) => ({
          ...prev,
          [templateId]: {
            ...prev[templateId],
            status: data.status,
            progress: data.progress,
            error: data.error,
            results: data.results,
          },
        }));

        if (data.status !== 'running') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Error polling job status:', error);
        clearInterval(pollInterval);
      }
    }, 2000);
  };

  const viewResults = (results: TemplateRunResult[]) => {
    setSelectedResults(results);
    setShowResults(true);
  };

  const getStatusChip = (status: string) => {
    const statusConfig: Record<string, { color: any; label: string }> = {
      idle: { color: 'default', label: 'Inactivo' },
      running: { color: 'primary', label: 'En Ejecución' },
      completed: { color: 'success', label: 'Completado' },
      error: { color: 'error', label: 'Error' },
    };

    const config = statusConfig[status] || statusConfig.idle;

    return <Chip size="small" color={config.color} label={config.label} />;
  };

  return (
    <Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Template</TableCell>
              <TableCell>URL</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Progreso</TableCell>
              <TableCell align="right">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.map((template) => {
              const status = template.id ? jobStatuses[template.id] : undefined;
              return (
                <TableRow key={template.id}>
                  <TableCell>{template.name}</TableCell>
                  <TableCell>{template.url}</TableCell>
                  <TableCell>
                    {status ? getStatusChip(status.status) : '-'}
                  </TableCell>
                  <TableCell>
                    {status?.status === 'running' && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={20} />
                        {status.progress !== undefined && (
                          <Typography variant="body2">
                            {Math.round(status.progress)}%
                          </Typography>
                        )}
                      </Box>
                    )}
                    {status?.status === 'error' && (
                      <Typography color="error" variant="body2">
                        {status.error}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    {status?.status === 'idle' && (
                      <Tooltip title="Iniciar">
                        <IconButton
                          color="primary"
                          onClick={() => template.id && startScraping(template.id)}
                        >
                          <PlayIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {status?.status === 'running' && (
                      <Tooltip title="Detener">
                        <IconButton
                          color="error"
                          onClick={() => template.id && stopScraping(template.id)}
                        >
                          <StopIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {status?.results && status.results.length > 0 && (
                      <Tooltip title="Ver Resultados">
                        <IconButton
                          onClick={() => viewResults(status.results!)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Modal de Resultados */}
      {showResults && (
        <Paper
          sx={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '80%',
            maxHeight: '80vh',
            overflow: 'auto',
            p: 3,
            zIndex: 1000,
          }}
        >
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="h6">Resultados del Scraping</Typography>
            <Button onClick={() => setShowResults(false)}>Cerrar</Button>
          </Box>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Fecha</TableCell>
                  <TableCell>URL</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Datos</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {selectedResults.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      {new Date(result.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>{result.url}</TableCell>
                    <TableCell>
                      {result.success ? (
                        <Chip
                          size="small"
                          color="success"
                          label="Éxito"
                        />
                      ) : (
                        <Chip
                          size="small"
                          color="error"
                          label={result.error || 'Error'}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <pre
                        style={{
                          margin: 0,
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word',
                        }}
                      >
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
};

export default RunTemplates;
