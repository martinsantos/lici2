import axios, { AxiosError } from 'axios';

// Tipos
export interface UploadResponse {
  success: boolean;
  files?: Array<{
    filename: string;
    document_id: number;
    file_location: string;
  }>;
  error?: string;
}

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// Configuración
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:4322';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_MIME_TYPES = ['application/pdf', 'image/jpeg', 'image/png'];

// Instancia de Axios configurada
const uploadInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  validateStatus: (status) => status < 500, // Tratar 500s como errores de red
});

// Funciones auxiliares
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const validateFile = (file: File): string | null => {
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    return `Tipo de archivo no permitido: ${file.type}. Solo se permiten: ${ALLOWED_MIME_TYPES.join(', ')}`;
  }
  if (file.size > MAX_FILE_SIZE) {
    return `Archivo demasiado grande: ${(file.size / 1024 / 1024).toFixed(2)}MB. Máximo permitido: ${MAX_FILE_SIZE / 1024 / 1024}MB`;
  }
  return null;
};

const createFormData = (files: File[]): FormData => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  return formData;
};

// Función principal de carga
export const uploadFiles = async (
  files: File[],
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResponse> => {
  // Validación inicial
  for (const file of files) {
    const error = validateFile(file);
    if (error) {
      return { success: false, error };
    }
  }

  const formData = createFormData(files);
  let retryCount = 0;

  while (retryCount < MAX_RETRIES) {
    try {
      console.log('Intentando subir archivos...');
      
      const response = await uploadInstance.post('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            onProgress({
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage: Math.round((progressEvent.loaded * 100) / progressEvent.total),
            });
          }
        },
      });

      console.log('Respuesta del servidor:', response.data);

      if (response.status === 200 && response.data?.files) {
        return {
          success: true,
          files: response.data.files,
        };
      }

      throw new Error(response.data?.detail || 'Error desconocido en la carga de archivos');

    } catch (error) {
      console.error('Error en la carga:', error);
      
      const axiosError = error as AxiosError<any>;
      
      // Determinar si debemos reintentar
      const shouldRetry = (
        retryCount < MAX_RETRIES &&
        (!axiosError.response || axiosError.response.status >= 500)
      );

      if (shouldRetry) {
        retryCount++;
        console.log(`Reintentando en ${RETRY_DELAY * retryCount}ms... (intento ${retryCount}/${MAX_RETRIES})`);
        await delay(RETRY_DELAY * retryCount);
        continue;
      }

      // Construir mensaje de error apropiado
      let errorMessage = 'Error al subir los archivos';
      
      if (axiosError.response) {
        const data = axiosError.response.data;
        errorMessage = data?.detail || data?.message || `Error ${axiosError.response.status}`;
      } else if (axiosError.request) {
        errorMessage = 'Error de conexión con el servidor';
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  return {
    success: false,
    error: 'No se pudo completar la carga después de varios intentos',
  };
};
