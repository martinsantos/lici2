import type { APIRoute } from 'astro';
import prisma from '../../../lib/prisma';

export const GET: APIRoute = async () => {
  try {
    // Recuperar todas las licitaciones, ordenadas por fecha de publicación más reciente
    const licitaciones = await prisma.licitacion.findMany({
      orderBy: {
        fechaPublicacion: 'desc'
      }
    });

    return new Response(JSON.stringify(licitaciones), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error al recuperar licitaciones:', error);
    return new Response(JSON.stringify({ 
      error: 'No se pudieron recuperar las licitaciones',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const POST: APIRoute = async ({ request }) => {
  try {
    const data = await request.json();
    console.log('Received data:', data);

    // Validar y formatear las fechas
    const formatDate = (dateString: string) => {
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
          throw new Error('Fecha inválida');
        }
        return date;
      } catch (error) {
        console.error('Error parsing date:', dateString, error);
        throw new Error(`Error al procesar la fecha: ${dateString}`);
      }
    };

    // Crear el objeto de licitación con los campos requeridos
    const licitacion = {
      titulo: data.titulo,
      descripcion: data.descripcion,
      fechaPublicacion: formatDate(data.fechaPublicacion),
      fechaApertura: formatDate(data.fechaApertura),
      numeroExpediente: data.numeroExpediente || '',
      numeroLicitacion: data.numeroLicitacion || '',
      organismo: data.organismo,
      contacto: data.contacto || '',
      monto: Number(data.monto) || 0,
      estado: data.estado || 'Pendiente',
      categoria: data.categoria || '',
      ubicacion: data.ubicacion || '',
      plazo: data.plazo || '',
      requisitos: data.requisitos || [],
      garantia: data.garantia || '',
      documentos: data.documentos || [],
      presupuesto: Number(data.presupuesto) || 0,
      moneda: data.moneda || 'ARS',
      idioma: data.idioma || 'es',
      etapa: data.etapa || '',
      modalidad: data.modalidad || '',
      area: data.area || '',
      existe: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    console.log('Processed licitacion data:', licitacion);

    // Crear la licitación en la base de datos
    const createdLicitacion = await prisma.licitacion.create({
      data: licitacion
    });

    console.log('Created licitacion:', createdLicitacion);

    return new Response(JSON.stringify(createdLicitacion), {
      status: 201,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error creating licitacion:', error);
    return new Response(JSON.stringify({
      error: 'Error al crear la licitación',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
