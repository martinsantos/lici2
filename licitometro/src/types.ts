export interface Contacto {
  nombre: string;
  email: string;
  telefono: string;
}

export interface Garantia {
  tipo: string;
  monto: string;
  plazo: string;
}

export interface Documento {
  id: number;
  nombre: string;
  tipo: string;
  url: string;
  licitacion_id?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Licitacion {
  id: number;
  titulo: string;
  descripcion: string;
  fechaPublicacion: Date | string;
  fechaApertura: Date | string | null;
  numeroExpediente: string | null;
  numeroLicitacion: string | null;
  organismo: string | null;
  contacto: string | null;
  monto: number | null;
  estado: string | null;
  categoria: string | null;
  ubicacion: string | null;
  plazo: string | null;
  requisitos: string[];
  garantia: string | null;
  documentos: Documento[];
  presupuesto: number | null;
  moneda: string | null;
  idioma: string | null;
  etapa: string | null;
  modalidad: string | null;
  area: string | null;
  existe: boolean;
  createdAt: Date;
  updatedAt: Date;
  archivosAdjuntos?: File[];
}
