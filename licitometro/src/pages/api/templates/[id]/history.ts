import type { APIRoute } from 'astro';
import { getTemplateHistory } from '../../../../lib/templates';
import { isAuthenticated } from '../../../../lib/auth';

export const get: APIRoute = async ({ params, request }) => {
  try {
    // Verificar autenticación
    const authResult = await isAuthenticated(request);
    if (!authResult.authenticated) {
      return new Response(JSON.stringify({ error: 'No autorizado' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { id } = params;
    if (!id) {
      return new Response(JSON.stringify({ error: 'ID de plantilla no proporcionado' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Obtener el historial de ejecuciones
    const history = await getTemplateHistory(id);

    return new Response(JSON.stringify({ runs: history }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error getting template history:', error);
    return new Response(JSON.stringify({ error: 'Error interno del servidor' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
