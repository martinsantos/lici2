import type { APIRoute } from 'astro';
import prisma from '../../../../../../lib/prisma';
import path from 'path';
import fs from 'fs/promises';

export const GET: APIRoute = async ({ params, request }) => {
  try {
    const { id, filename } = params;
    const numericId = parseInt(id || '', 10);

    if (isNaN(numericId)) {
      return new Response('ID de licitación inválido', { status: 400 });
    }

    // Verificar que la licitación existe
    const licitacion = await prisma.licitacion.findUnique({
      where: { id: numericId },
      select: { documentos: true }
    });

    if (!licitacion) {
      return new Response('Licitación no encontrada', { status: 404 });
    }

    // Verificar que el archivo está registrado en la base de datos
    const documentos = Array.isArray(licitacion.documentos) ? licitacion.documentos : [];
    const documento = documentos.find(doc => 
      (typeof doc === 'string' && doc.includes(filename)) ||
      (typeof doc === 'object' && doc.filename === filename)
    );

    if (!documento) {
      return new Response('Archivo no encontrado en la base de datos', { status: 404 });
    }

    // Construir la ruta al archivo
    const filePath = path.join(process.cwd(), 'public', 'uploads', 'licitaciones', id, filename);

    try {
      // Verificar que el archivo existe
      await fs.access(filePath);
      
      // Leer el archivo
      const file = await fs.readFile(filePath);
      
      // Determinar el tipo MIME
      const ext = path.extname(filename).toLowerCase();
      const mimeTypes: { [key: string]: string } = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
      };

      const contentType = mimeTypes[ext] || 'application/octet-stream';

      // Devolver el archivo con el tipo MIME correcto
      return new Response(file, {
        headers: {
          'Content-Type': contentType,
          'Content-Disposition': `inline; filename="${filename}"`,
        },
      });
    } catch (error) {
      console.error('Error accessing file:', error);
      return new Response('Archivo no encontrado en el sistema de archivos', { status: 404 });
    }
  } catch (error) {
    console.error('Error handling file request:', error);
    return new Response('Error interno del servidor', { status: 500 });
  }
};
