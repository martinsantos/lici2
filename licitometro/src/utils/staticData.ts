import type { Licitacion } from '../types';
import prisma from '../lib/prisma';

// Tipos personalizados para el manejo de errores y respuestas
type ApiResponse<T> = {
  status: 'ok' | 'error';
  data: T;
  message?: string;
};

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Función helper para manejar las peticiones a la API
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  // Determine base URL dynamically
  const baseUrl = typeof window !== 'undefined' 
    ? window.location.origin 
    : import.meta.env.PUBLIC_API_BASE_URL || 'http://localhost:3004';
  
  const apiUrl = `${baseUrl}/api/v1${endpoint}`;
  
  console.log(`[FETCH] Attempting to fetch: ${apiUrl}`);
  console.log(`[FETCH] Current environment: ${typeof window !== 'undefined' ? 'Browser' : 'Server'}`);
  
  try {
    const defaultOptions: RequestInit = {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      ...options,
    };

    console.log(`[FETCH] Request options:`, JSON.stringify(defaultOptions, null, 2));

    const response = await fetch(apiUrl, defaultOptions);
    
    console.log(`[FETCH] Response status: ${response.status}`);

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(`[FETCH] API Error: ${response.status} - ${errorBody}`);
      throw new ApiError(
        response.status,
        `HTTP error! status: ${response.status}`,
        errorBody
      );
    }

    const data = await response.json();
    console.log('[FETCH] Successful response:', JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.error('[FETCH] Detailed fetch error:', error);
    throw error;
  }
}

export async function getAllLicitaciones(): Promise<Licitacion[]> {
  try {
    console.log('[LICITACIONES] Intentando obtener todas las licitaciones desde la base de datos');
    const licitaciones = await prisma.licitacion.findMany({
      orderBy: {
        fechaPublicacion: 'desc'
      }
    });
    
    console.log(`[LICITACIONES] Se encontraron ${licitaciones?.length || 0} licitaciones`);
    
    if (!licitaciones || !Array.isArray(licitaciones)) {
      console.error('[LICITACIONES] Respuesta inválida:', licitaciones);
      return [];
    }

    // Log primera licitación para debugging
    if (licitaciones.length > 0) {
      console.log('[LICITACIONES] Primera licitación:', JSON.stringify(licitaciones[0], null, 2));
    }

    return licitaciones;
  } catch (error) {
    console.error('[LICITACIONES] Error al obtener licitaciones:', error);
    return [];
  }
}

export async function getLicitacionById(id: string): Promise<Licitacion | null> {
  try {
    console.log(`[LICITACION] Fetching licitacion with ID: ${id}`);
    const licitacion = await fetchApi<Licitacion>(`/licitaciones/${id}`);
    
    if (!licitacion) {
      console.error(`[LICITACION] No licitacion found with ID: ${id}`);
      return null;
    }

    console.log('[LICITACION] Fetched details:', JSON.stringify(licitacion, null, 2));
    return licitacion;
  } catch (error) {
    console.error(`[LICITACION] Error fetching licitacion with ID ${id}:`, error);
    return null;
  }
}

// Función para validar una licitación
export function validateLicitacion(licitacion: Partial<Licitacion>): boolean {
  const requiredFields = [
    'titulo',
    'descripcion',
    'estado',
    'organismo',
    'presupuesto',
    'moneda',
    'fechaPublicacion',
    'fechaApertura'
  ];

  return requiredFields.every(field => {
    const value = licitacion[field as keyof Licitacion];
    return value !== undefined && value !== null && value !== '';
  });
}
