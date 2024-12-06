import type { APIRoute } from 'astro';
import prisma from '../../../../../lib/prisma';

export const DELETE: APIRoute = async ({ params }) => {
  try {
    const { id } = params;

    if (!id) {
      return new Response(JSON.stringify({ error: 'ID no proporcionado' }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }

    // Soft delete: actualizamos el campo 'existe' a false en lugar de eliminar el registro
    await prisma.licitacion.update({
      where: { id },
      data: { existe: false }
    });

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error al eliminar la licitación:', error);
    return new Response(JSON.stringify({ error: 'Error al eliminar la licitación' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
