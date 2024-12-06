import type { APIRoute } from 'astro';
import prisma from '../../lib/prisma';
import { Licitacion } from '../../types';

export const POST: APIRoute = async ({ request }) => {
  try {
    const licitacionData: Partial<Licitacion> = await request.json();

    // Validar datos de entrada
    if (!licitacionData.titulo || !licitacionData.descripcion) {
      return new Response(JSON.stringify({ 
        error: 'Título y descripción son obligatorios' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Crear licitación en la base de datos
    const nuevaLicitacion = await prisma.licitacion.create({
      data: {
        titulo: licitacionData.titulo,
        descripcion: licitacionData.descripcion,
        fechaPublicacion: licitacionData.fechaPublicacion 
          ? new Date(licitacionData.fechaPublicacion) 
          : new Date(),
        fechaApertura: licitacionData.fechaApertura 
          ? new Date(licitacionData.fechaApertura) 
          : undefined,
        numeroExpediente: licitacionData.numeroExpediente || '',
        numeroLicitacion: licitacionData.numeroLicitacion || '',
        organismo: licitacionData.organismo || '',
        contacto: licitacionData.contacto || '',
        monto: licitacionData.monto || 0,
        estado: licitacionData.estado || 'Pendiente',
        categoria: licitacionData.categoria || '',
        ubicacion: licitacionData.ubicacion || '',
        plazo: licitacionData.plazo || '',
        requisitos: licitacionData.requisitos || [],
        garantia: licitacionData.garantia || '',
        documentos: licitacionData.documentos || [],
        presupuesto: licitacionData.presupuesto || 0,
        moneda: licitacionData.moneda || 'ARS',
        idioma: licitacionData.idioma || 'es',
        etapa: licitacionData.etapa || '',
        modalidad: licitacionData.modalidad || '',
        area: licitacionData.area || '',
      }
    });

    // Manejar archivos adjuntos (pendiente de implementación completa)
    // Aquí deberías implementar la lógica de subida de archivos

    return new Response(JSON.stringify(nuevaLicitacion), {
      status: 201,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error al crear licitación:', error);
    return new Response(JSON.stringify({ 
      error: 'Error al crear la licitación',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
