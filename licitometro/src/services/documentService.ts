import { Documento } from '../types';
import { API_BASE_URL } from '../config';

class DocumentService {
  private static instance: DocumentService;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = API_BASE_URL;
  }

  public static getInstance(): DocumentService {
    if (!DocumentService.instance) {
      DocumentService.instance = new DocumentService();
    }
    return DocumentService.instance;
  }

  async uploadDocument(file: File, licitacionId: number): Promise<Documento> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/documents/upload/${licitacionId}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Error al subir el documento');
    }

    return response.json();
  }

  async deleteDocument(documentId: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/documents/${documentId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Error al eliminar el documento');
    }
  }

  getDocumentUrl(documento: Documento): string {
    if (!documento?.id) {
      throw new Error('ID del documento no disponible');
    }

    return `${this.baseUrl}/api/documents/download/${documento.id}`;
  }
}

export default DocumentService;
