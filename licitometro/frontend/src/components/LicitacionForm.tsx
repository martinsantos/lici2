import React, { useState } from 'react';
import { Box, Button, CircularProgress, Typography, Alert } from '@mui/material';
import { uploadFiles } from '../services/fileUploadService';

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  success: boolean;
  files: Array<{
    filename: string;
    url: string;
    id: string;
  }> | null;
}

export const LicitacionForm: React.FC = () => {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    success: false,
    files: null
  });

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
      success: false,
      files: null
    });

    try {
      const result = await uploadFiles(files, (progress) => {
        setUploadState(prev => ({
          ...prev,
          progress: progress.percentage
        }));
      });

      if (result.success && result.files) {
        setUploadState({
          isUploading: false,
          progress: 100,
          error: null,
          success: true,
          files: result.files
        });
      } else {
        setUploadState({
          isUploading: false,
          progress: 0,
          error: result.error || 'Error desconocido al subir archivos',
          success: false,
          files: null
        });
      }
    } catch (error) {
      setUploadState({
        isUploading: false,
        progress: 0,
        error: 'Error inesperado al subir archivos',
        success: false,
        files: null
      });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Subir Archivos
      </Typography>
      
      <Box sx={{ my: 2 }}>
        <input
          accept="application/pdf,image/*"
          style={{ display: 'none' }}
          id="upload-file"
          type="file"
          multiple
          onChange={handleFileChange}
          disabled={uploadState.isUploading}
        />
        <label htmlFor="upload-file">
          <Button
            variant="contained"
            component="span"
            disabled={uploadState.isUploading}
          >
            {uploadState.isUploading ? 'Subiendo...' : 'Seleccionar Archivos'}
          </Button>
        </label>
      </Box>

      {uploadState.isUploading && (
        <Box sx={{ my: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <CircularProgress variant="determinate" value={uploadState.progress} size={24} />
          <Typography variant="body2" color="text.secondary">
            {uploadState.progress}% completado
          </Typography>
        </Box>
      )}

      {uploadState.error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {uploadState.error}
        </Alert>
      )}

      {uploadState.success && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Archivos subidos exitosamente
          {uploadState.files && (
            <Box component="ul" sx={{ mt: 1, pl: 2 }}>
              {uploadState.files.map((file, index) => (
                <li key={file.id || index}>
                  {file.filename}
                </li>
              ))}
            </Box>
          )}
        </Alert>
      )}
    </Box>
  );
};
