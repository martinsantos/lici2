import type { APIRoute } from 'astro';
import prisma from '../../../../lib/prisma';

export const GET: APIRoute = async ({ params }) => {
  try {
    const { id } = params;

    if (!id) {
      return new Response(JSON.stringify({ 
        error: 'ID de licitación no proporcionado' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Convertir ID a número
    const numericId = parseInt(id, 10);
    if (isNaN(numericId)) {
      return new Response(JSON.stringify({ 
        error: 'ID de licitación inválido' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const licitacion = await prisma.licitacion.findUnique({
      where: { 
        id: numericId
      }
    });

    if (!licitacion) {
      return new Response(JSON.stringify({ 
        error: 'Licitación no encontrada' 
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify(licitacion), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error al recuperar licitación:', error);
    return new Response(JSON.stringify({ 
      error: 'No se pudo recuperar la licitación',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const PUT: APIRoute = async ({ params, request }) => {
  try {
    const { id } = params;

    if (!id) {
      return new Response(JSON.stringify({ 
        error: 'ID de licitación no proporcionado' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Convertir ID a número
    const numericId = parseInt(id, 10);
    if (isNaN(numericId)) {
      return new Response(JSON.stringify({ 
        error: 'ID de licitación inválido' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const body = await request.json();

    // Validar fechas
    const fechaPublicacion = body.fechaPublicacion ? new Date(body.fechaPublicacion) : undefined;
    const fechaApertura = body.fechaApertura ? new Date(body.fechaApertura) : undefined;

    // Validar que fechaPublicacion sea anterior a fechaApertura
    if (fechaPublicacion && fechaApertura && fechaPublicacion > fechaApertura) {
      return new Response(JSON.stringify({
        error: 'La fecha de publicación debe ser anterior a la fecha de apertura'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Verificar que la licitación existe
    const existingLicitacion = await prisma.licitacion.findUnique({
      where: { id: numericId }
    });

    if (!existingLicitacion) {
      return new Response(JSON.stringify({ 
        error: 'Licitación no encontrada' 
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Actualizar la licitación
    const licitacionActualizada = await prisma.licitacion.update({
      where: { 
        id: numericId
      },
      data: {
        titulo: body.titulo,
        descripcion: body.descripcion,
        organismo: body.organismo,
        presupuesto: body.presupuesto ? parseFloat(body.presupuesto) : undefined,
        moneda: body.moneda,
        estado: body.estado,
        fechaPublicacion: fechaPublicacion,
        fechaApertura: fechaApertura,
        ubicacion: body.ubicacion,
        requisitos: body.requisitos,
        documentos: body.documentos,
        updatedAt: new Date()
      }
    });

    return new Response(JSON.stringify(licitacionActualizada), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error al actualizar licitación:', error);
    return new Response(JSON.stringify({ 
      error: 'No se pudo actualizar la licitación',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const DELETE: APIRoute = async ({ params }) => {
  try {
    const { id } = params;

    if (!id) {
      return new Response(JSON.stringify({ 
        error: 'ID de licitación no proporcionado' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Convertir ID a número
    const numericId = parseInt(id, 10);
    if (isNaN(numericId)) {
      return new Response(JSON.stringify({ 
        error: 'ID de licitación inválido' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Primero verificar si la licitación existe
    const existingLicitacion = await prisma.licitacion.findUnique({
      where: { id: numericId }
    });

    if (!existingLicitacion) {
      return new Response(JSON.stringify({ 
        error: 'Licitación no encontrada' 
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Eliminar la licitación
    await prisma.licitacion.delete({
      where: { id: numericId }
    });

    return new Response(JSON.stringify({ 
      message: 'Licitación eliminada exitosamente' 
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error al eliminar licitación:', error);
    return new Response(JSON.stringify({ 
      error: 'No se pudo eliminar la licitación',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
