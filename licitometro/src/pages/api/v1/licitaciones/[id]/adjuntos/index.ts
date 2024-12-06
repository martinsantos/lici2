import type { APIRoute } from 'astro';
import prisma from '../../../../../../lib/prisma';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Función para asegurar que el directorio existe
async function ensureDir(dir: string) {
  try {
    await fs.access(dir);
  } catch {
    await fs.mkdir(dir, { recursive: true });
  }
}

export const POST: APIRoute = async ({ params, request }) => {
  try {
    console.log('Iniciando proceso de subida de archivos');
    const { id } = params;
    const numericId = parseInt(id || '', 10);

    if (isNaN(numericId)) {
      console.error('ID inválido:', id);
      return new Response(JSON.stringify({
        success: false,
        error: 'ID de licitación inválido'
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Verificar que la licitación existe
    console.log('Buscando licitación:', numericId);
    const licitacion = await prisma.licitacion.findUnique({
      where: { id: numericId }
    });

    if (!licitacion) {
      console.error('Licitación no encontrada:', numericId);
      return new Response(JSON.stringify({
        success: false,
        error: 'Licitación no encontrada'
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Procesar el formulario multipart
    console.log('Procesando formulario multipart');
    const formData = await request.formData();
    const files = formData.getAll('files');

    if (!files.length) {
      console.error('No se encontraron archivos en el formulario');
      return new Response(JSON.stringify({
        success: false,
        error: 'No se encontraron archivos'
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    console.log(`Procesando ${files.length} archivos`);

    // Crear directorios necesarios
    const publicDir = path.join(process.cwd(), 'public');
    const uploadsBaseDir = path.join(publicDir, 'uploads');
    const licitacionesDir = path.join(uploadsBaseDir, 'licitaciones');
    const licitacionDir = path.join(licitacionesDir, id.toString());

    // Asegurar que todos los directorios existen
    await ensureDir(publicDir);
    await ensureDir(uploadsBaseDir);
    await ensureDir(licitacionesDir);
    await ensureDir(licitacionDir);

    console.log('Directorio de subida:', licitacionDir);

    const fileUrls: string[] = [];
    const fileResults = [];

    // Procesar cada archivo
    for (const file of files) {
      if (file instanceof File) {
        console.log('Procesando archivo:', file.name);
        
        try {
          const buffer = Buffer.from(await file.arrayBuffer());
          const originalFilename = file.name;
          // Limpiar el nombre del archivo
          const safeFilename = originalFilename.replace(/[^a-zA-Z0-9.-]/g, '_');
          const timestamp = Date.now();
          const uniqueFilename = `${timestamp}-${safeFilename}`;
          const filePath = path.join(licitacionDir, uniqueFilename);

          console.log('Guardando archivo en:', filePath);
          await fs.writeFile(filePath, buffer);

          const fileUrl = `/uploads/licitaciones/${id}/${encodeURIComponent(uniqueFilename)}`;
          fileUrls.push(fileUrl);

          const fileInfo = {
            originalName: originalFilename,
            filename: uniqueFilename,
            path: fileUrl,
            size: buffer.length,
            type: file.type,
            uploadedAt: new Date().toISOString()
          };

          fileResults.push(fileInfo);
          console.log('Archivo procesado exitosamente:', fileInfo);
        } catch (error) {
          console.error('Error procesando archivo:', file.name, error);
          throw new Error(`Error al procesar el archivo ${file.name}`);
        }
      }
    }

    // Actualizar la licitación con los nuevos archivos
    console.log('Actualizando licitación con nuevos archivos');
    try {
      const currentDocs = Array.isArray(licitacion.documentos) ? licitacion.documentos : [];
      await prisma.licitacion.update({
        where: { id: numericId },
        data: {
          documentos: [...currentDocs, ...fileUrls]
        }
      });
    } catch (error) {
      console.error('Error al actualizar la licitación en la base de datos:', error);
      throw new Error('Error al guardar la información de los archivos en la base de datos');
    }

    console.log('Proceso completado exitosamente');
    return new Response(JSON.stringify({ 
      success: true,
      files: fileResults
    }), {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Error en el proceso de subida:', error);
    return new Response(JSON.stringify({
      success: false,
      error: error instanceof Error ? error.message : 'Error interno del servidor'
    }), { 
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
