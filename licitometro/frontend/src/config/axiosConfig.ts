import axios from 'axios';

// Crear una instancia específica para carga de archivos
const uploadInstance = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || 'http://localhost:4322',
  timeout: 300000, // 5 minutes
  maxContentLength: Infinity,
  maxBodyLength: Infinity,
  validateStatus: status => status < 500,
  headers: {
    'Accept': 'application/json',
    'Cache-Control': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// Instancia general para otras peticiones
const instance = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || 'http://localhost:4322',
  timeout: 300000,
  maxContentLength: Infinity,
  maxBodyLength: Infinity,
  validateStatus: status => status < 500,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor de solicitud para la instancia de carga
uploadInstance.interceptors.request.use(
  (config) => {
    const method = config.method?.toUpperCase() || 'UNKNOWN';
    const url = config.url || 'UNKNOWN';
    
    console.log(`[UPLOAD ${method}] ${url} Request:`, {
      headers: config.headers,
      data: config.data instanceof FormData ? 'FormData (files)' : config.data
    });

    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    return config;
  },
  (error) => {
    console.error('Upload request error:', error);
    return Promise.reject(error);
  }
);

// Interceptor de respuesta para la instancia de carga
uploadInstance.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase() || 'UNKNOWN';
    const url = response.config.url || 'UNKNOWN';
    
    console.log(`[UPLOAD ${method}] ${url} Response:`, {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    });
    
    return response;
  },
  (error) => {
    console.error('Upload response error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    
    // Si no hay respuesta del servidor, crear una respuesta de error
    if (!error.response) {
      error.response = {
        status: 500,
        data: {
          error: true,
          message: 'Error de conexión con el servidor'
        }
      };
    }
    
    return Promise.reject(error);
  }
);

// Interceptores para la instancia general
instance.interceptors.request.use(
  (config) => {
    const method = config.method?.toUpperCase() || 'UNKNOWN';
    const url = config.url || 'UNKNOWN';
    
    console.log(`[${method}] ${url} Request:`, {
      headers: config.headers,
      data: config.data
    });

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase() || 'UNKNOWN';
    const url = response.config.url || 'UNKNOWN';
    
    console.log(`[${method}] ${url} Response:`, {
      status: response.status,
      data: response.data
    });
    
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    return Promise.reject(error);
  }
);

export { uploadInstance };
export default instance;
