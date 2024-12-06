import { join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

export const UPLOADS_CONFIG = {
  // Directorio donde se guardarán los archivos
  uploadDir: join(__dirname, '..', '..', 'public', 'uploads'),
  
  // URL base para acceder a los archivos
  baseUrl: '/uploads',
  
  // Tipos de archivos permitidos
  allowedTypes: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
    'image/gif'
  ],
  
  // Tamaño máximo del archivo en bytes (50MB)
  maxFileSize: 50 * 1024 * 1024,
  
  // Función para generar un nombre de archivo único
  generateFileName: (originalName: string): string => {
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 15);
    const extension = originalName.split('.').pop();
    return `${timestamp}-${randomString}.${extension}`;
  }
};
