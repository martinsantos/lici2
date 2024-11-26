// Configuración base para la API
const API_BASE_URL = import.meta.env.PUBLIC_API_URL || '/api';

interface ApiOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function api(endpoint: string, options: ApiOptions = {}) {
  const {
    method = 'GET',
    body,
    headers = {},
  } = options;

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    credentials: 'same-origin', // Importante para cookies de sesión
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
      console.error('API Error:', {
        status: response.status,
        endpoint,
        errorData
      });
      throw new ApiError(response.status, errorData.message || `Error ${response.status}`);
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('API Request Failed:', {
      endpoint,
      error
    });
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Error de conexión al servidor');
  }
}
