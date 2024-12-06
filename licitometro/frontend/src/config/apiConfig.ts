// API Base URLs
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:3003';
const API_VERSION = 'v1';

export const API_ENDPOINTS = {
  // Licitaciones
  LICITACIONES: {
    BASE: `/api/${API_VERSION}/licitaciones`,
    CREATE: `/api/${API_VERSION}/licitaciones/create`,
    UPDATE: (id: number) => `/api/${API_VERSION}/licitaciones/${id}`,
    DELETE: (id: number) => `/api/${API_VERSION}/licitaciones/${id}`,
    GET_ALL: `/api/${API_VERSION}/licitaciones`,
    GET_BY_ID: (id: number) => `/api/${API_VERSION}/licitaciones/${id}`,
    SEARCH: `/api/${API_VERSION}/licitaciones/search`,
  },

  // Documentos
  DOCUMENTS: {
    UPLOAD: `/api/${API_VERSION}/upload`,  
    DELETE: (id: number) => `/api/${API_VERSION}/documents/${id}`,
    DOWNLOAD: (id: number) => `/api/${API_VERSION}/documents/${id}/download`,
  },

  // RECON Templates
  TEMPLATES: {
    BASE: `/api/${API_VERSION}/templates`,
    CREATE: `/api/${API_VERSION}/templates/create`,
    UPDATE: (id: number) => `/api/${API_VERSION}/templates/${id}`,
    DELETE: (id: number) => `/api/${API_VERSION}/templates/${id}`,
    GET_ALL: `/api/${API_VERSION}/templates`,
    GET_BY_ID: (id: number) => `/api/${API_VERSION}/templates/${id}`,
  },

  // Features
  FEATURES: {
    BASE: `/api/${API_VERSION}/features`,
    CREATE: `/api/${API_VERSION}/features/create`,
    UPDATE: (id: number) => `/api/${API_VERSION}/features/${id}`,
    DELETE: (id: number) => `/api/${API_VERSION}/features/${id}`,
    GET_ALL: `/api/${API_VERSION}/features`,
    GET_BY_TEMPLATE: (templateId: number) => `/api/${API_VERSION}/features/template/${templateId}`,
  },
};

interface UploadConfig {
  MAX_FILE_SIZE: number;
  MAX_FILES: number;
  ALLOWED_FILE_TYPES: string[];
  TIMEOUT?: number;
}

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: parseInt(process.env.VITE_API_TIMEOUT || '10000', 10),
  RETRY_ATTEMPTS: parseInt(process.env.VITE_API_RETRY_ATTEMPTS || '3', 10),
  RETRY_DELAY: parseInt(process.env.VITE_API_RETRY_DELAY || '1000', 10),
  
  UPLOAD_CONFIG: {
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB por defecto
    MAX_FILES: 5, // Máximo 5 archivos por carga
    ALLOWED_FILE_TYPES: [
      'application/pdf',
      'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg', 
      'image/png',
      '.pdf', 
      '.doc', 
      '.docx', 
      '.jpg', 
      '.jpeg', 
      '.png'
    ],
    TIMEOUT: 10000 // 10 segundos por defecto
  },
  ENDPOINTS: {
    DOCUMENTS: {
      UPLOAD: '/api/v1/documents/upload_multiple_files',
      GET_ALL: '/api/v1/documents',
      DELETE: (id: string) => `/api/v1/documents/${id}`,
    },
    LICITACIONES: {
      CREATE: '/api/v1/licitaciones',
      GET_ALL: '/api/v1/licitaciones',
      GET_ONE: (id: string) => `/api/v1/licitaciones/${id}`,
      UPDATE: (id: string) => `/api/v1/licitaciones/${id}`,
      DELETE: (id: string) => `/api/v1/licitaciones/${id}`,
    }
  },
};

export default {
  API_ENDPOINTS,
  API_CONFIG,
};
