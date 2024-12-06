import React, { useState } from 'react';
import { FileUploadResponse, uploadFiles } from '../../services/fileUploadService';
import { 
  Box, 
  Button, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  Alert 
} from '@mui/material';

interface LicitacionFormProps {
  // Add any necessary props
}

const LicitacionForm: React.FC<LicitacionFormProps> = () => {
  const [archivos, setArchivos] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<FileUploadResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleArchivoChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    // Convert FileList to array
    const newFiles = Array.from(files);

    try {
      // Start upload process
      setIsUploading(true);
      setError(null);

      // Use the uploadFiles service (which now handles validation internally)
      const uploadedFilesResponse = await uploadFiles(newFiles);
      
      // Update state with new files
      setArchivos(prevArchivos => [
        ...prevArchivos, 
        ...newFiles
      ]);

      // Update uploadedFiles state for display
      setUploadedFiles(prevUploadedFiles => [
        ...prevUploadedFiles,
        ...uploadedFilesResponse
      ]);

    } catch (error: any) {
      console.error('Error al subir archivos:', error);
      
      // Extraer información detallada del error
      const errorStatus = error.response?.status || 'unknown';
      const errorMessage = error.response?.data?.detail || 
                           error.response?.data?.message || 
                           error.message || 
                           'Error desconocido al subir archivos';
      
      // Log información detallada del error
      console.error('Error details:', {
        status: errorStatus,
        message: errorMessage,
        fullError: error
      });
      
      // Set user-friendly error message
      setError(`Error ${errorStatus}: ${errorMessage}`);
      
      // Optional: show alert to user
      alert(`Error al subir archivos: ${errorMessage}`);
    } finally {
      // Always reset uploading state
      setIsUploading(false);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    if (uploadedFiles.length === 0) {
      setError('Por favor, suba al menos un archivo antes de enviar.');
      return;
    }

    // Implement your form submission logic here
    console.log('Archivos subidos:', uploadedFiles);
    // TODO: Add actual form submission logic
  };

  const handleRemoveFile = (indexToRemove: number) => {
    setArchivos(prevArchivos => 
      prevArchivos.filter((_, index) => index !== indexToRemove)
    );
    setUploadedFiles(prevUploadedFiles => 
      prevUploadedFiles.filter((_, index) => index !== indexToRemove)
    );
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 600, margin: 'auto', padding: 2 }}>
      <input 
        type="file" 
        id="archivos" 
        multiple 
        onChange={handleArchivoChange} 
        style={{ display: 'none' }}
        disabled={isUploading}
      />
      <label htmlFor="archivos">
        <Button 
          variant="contained" 
          component="span" 
          disabled={isUploading}
        >
          {isUploading ? 'Subiendo...' : 'Seleccionar Archivos'}
        </Button>
      </label>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {uploadedFiles.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6">Archivos Subidos:</Typography>
          <List>
            {uploadedFiles.map((file, index) => (
              <ListItem 
                key={index} 
                secondaryAction={
                  <Button 
                    color="error" 
                    onClick={() => handleRemoveFile(index)}
                    disabled={isUploading}
                  >
                    Eliminar
                  </Button>
                }
              >
                <ListItemText 
                  primary={file.filename} 
                  secondary={`ID: ${file.document_id}`} 
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      <Button 
        type="submit" 
        variant="contained" 
        color="primary" 
        sx={{ mt: 2 }}
        disabled={uploadedFiles.length === 0 || isUploading}
      >
        Enviar
      </Button>
    </Box>
  );
};

export default LicitacionForm;
