import type { APIRoute } from 'astro';
import { getTemplateById, runTemplateJob } from '../../../../lib/templates';
import { isAuthenticated } from '../../../../lib/auth';

export const post: APIRoute = async ({ params, request }) => {
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

    // Obtener la plantilla
    const template = await getTemplateById(id);
    if (!template) {
      return new Response(JSON.stringify({ error: 'Plantilla no encontrada' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Iniciar el trabajo de scraping
    const job = await runTemplateJob(template);

    return new Response(JSON.stringify({
      jobId: job.id,
      status: job.status,
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error running template:', error);
    return new Response(JSON.stringify({ error: 'Error interno del servidor' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
