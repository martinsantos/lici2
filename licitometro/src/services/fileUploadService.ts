import axios from '../config/axiosConfig';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/plain',
  'image/jpeg',
  'image/png'
];

export const validateFile = (file: File): boolean => {
  if (file.size > MAX_FILE_SIZE) {
    console.warn(`File ${file.name} is too large (${file.size} bytes)`);
    return false;
  }

  if (!ALLOWED_FILE_TYPES.includes(file.type)) {
    console.warn(`File ${file.name} has invalid type (${file.type})`);
    return false;
  }

  return true;
};

export const uploadFiles = async (files: File[]): Promise<any[]> => {
  const validFiles = files.filter(validateFile);

  if (validFiles.length === 0) {
    throw new Error('No hay archivos válidos para subir');
  }

  const formData = new FormData();
  validFiles.forEach((file) => {
    formData.append('files', file);
  });

  try {
    const response = await axios.post('/api/v1/documents/upload_multiple_files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.files;
  } catch (error: any) {
    const status = error.response?.status || 'unknown';
    const detail = error.response?.data?.detail || error.message || 'Unknown error';
    throw new Error(`Error ${status}: ${detail}`);
  }
};
