import type { APIRoute } from 'astro';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { UPLOADS_CONFIG } from '../../../config/uploads';

export const POST: APIRoute = async ({ request }) => {
  try {
    if (!request.headers.get('content-type')?.includes('multipart/form-data')) {
      return new Response(JSON.stringify({ error: 'Content-Type debe ser multipart/form-data' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const formData = await request.formData();
    const files = formData.getAll('files');

    if (!files || files.length === 0) {
      return new Response(JSON.stringify({ error: 'No se encontraron archivos' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Crear directorio para archivos si no existe
    await mkdir(UPLOADS_CONFIG.uploadDir, { recursive: true });

    const urls: string[] = [];
    const errors: string[] = [];

    for (const file of files) {
      if (!(file instanceof File)) {
        errors.push(`El archivo ${file} no es válido`);
        continue;
      }

      // Validar tipo de archivo
      if (!UPLOADS_CONFIG.allowedTypes.includes(file.type)) {
        errors.push(`Tipo de archivo no permitido: ${file.type}`);
        continue;
      }

      // Validar tamaño
      if (file.size > UPLOADS_CONFIG.maxFileSize) {
        errors.push(`El archivo ${file.name} excede el tamaño máximo permitido de ${UPLOADS_CONFIG.maxFileSize / (1024 * 1024)}MB`);
        continue;
      }

      try {
        // Generar nombre único para el archivo
        const fileName = UPLOADS_CONFIG.generateFileName(file.name);
        const filePath = join(UPLOADS_CONFIG.uploadDir, fileName);

        // Guardar archivo
        const arrayBuffer = await file.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);
        await writeFile(filePath, buffer);

        // Agregar URL del archivo
        urls.push(`${UPLOADS_CONFIG.baseUrl}/${fileName}`);
      } catch (error) {
        console.error(`Error al procesar el archivo ${file.name}:`, error);
        errors.push(`Error al procesar el archivo ${file.name}`);
      }
    }

    // Si hay errores pero también se subieron algunos archivos exitosamente
    if (errors.length > 0 && urls.length > 0) {
      return new Response(JSON.stringify({ 
        success: false,
        urls,
        warnings: errors,
        message: 'Algunos archivos se subieron con éxito, pero hubo errores con otros'
      }), {
        status: 207,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }

    // Si solo hay errores
    if (errors.length > 0 && urls.length === 0) {
      return new Response(JSON.stringify({ 
        success: false,
        error: 'No se pudo procesar ningún archivo',
        details: errors
      }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }

    // Si todo fue exitoso
    return new Response(JSON.stringify({ 
      success: true,
      urls,
      message: 'Todos los archivos se subieron exitosamente'
    }), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    });
  } catch (error) {
    console.error('Error al procesar archivos:', error);
    return new Response(JSON.stringify({ 
      success: false,
      error: 'Error al procesar los archivos',
      details: error instanceof Error ? error.message : 'Error desconocido'
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      }
    });
  }
};

export const OPTIONS: APIRoute = async () => {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
};
