import type { Documento } from '../types';
import { apiClient } from './apiClient';

const BUCKET_NAME = import.meta.env.PUBLIC_MINIO_BUCKET || 'licitometro';

export class DocumentService {
  private static async handleResponse(response: any) {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error en la solicitud');
    }
    return response.data;
  }

  static async getUploadUrl(fileName: string, fileType: string): Promise<string> {
    const response = await apiClient('/api/documentos/upload-url', {
      method: 'POST',
      body: {
        fileName,
        fileType,
        bucket: BUCKET_NAME,
      },
    });

    return response.data.url;
  }

  static async uploadFile(file: File): Promise<Documento> {
    // 1. Get pre-signed URL
    const uploadUrl = await this.getUploadUrl(file.name, file.type);

    // 2. Upload to MinIO
    const uploadResponse = await fetch(uploadUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });

    if (!uploadResponse.ok) {
      throw new Error('Error al subir el archivo');
    }

    // 3. Register file in our database
    const fileData = {
      nombre: file.name,
      tipo: file.type.split('/')[1],
      tamaño: file.size,
      url: uploadUrl.split('?')[0], // Remove query parameters from URL
    };

    const registerResponse = await apiClient('/api/documentos', {
      method: 'POST',
      body: fileData,
    });

    return this.handleResponse(registerResponse);
  }

  static async deleteFile(id: string): Promise<void> {
    const response = await apiClient(`/api/documentos/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Error al eliminar el archivo');
    }
  }

  static async getDocumentos(): Promise<Documento[]> {
    const response = await apiClient('/api/documentos');
    return this.handleResponse(response);
  }

  static async getDocumento(id: string): Promise<Documento> {
    const response = await apiClient(`/api/documentos/${id}`);
    return this.handleResponse(response);
  }
}
