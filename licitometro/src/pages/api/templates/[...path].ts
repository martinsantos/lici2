import type { APIRoute } from 'astro';

// Proxy para el backend
const BACKEND_URL = 'http://localhost:8000';

export const all: APIRoute = async ({ request, params }) => {
  try {
    const path = params.path || '';
    const url = `${BACKEND_URL}/api/templates/${path}`;
    
    // Copiar el método y los headers
    const fetchOptions: RequestInit = {
      method: request.method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    // Si hay body, copiarlo
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      fetchOptions.body = await request.text();
    }

    const response = await fetch(url, fetchOptions);
    const data = await response.json();

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('API Error:', error);
    return new Response(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
};
