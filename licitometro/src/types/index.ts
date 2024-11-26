export interface Licitacion {
  id: string;
  titulo: string;
  descripcion: string;
  fechaPublicacion: Date;
  fechaCierre: Date;
  estado: 'abierta' | 'cerrada' | 'adjudicada' | 'desierta';
  presupuesto: number;
  entidad: string;
  documentos: Documento[];
  tags: string[];
}

export interface Documento {
  id: string;
  nombre: string;
  tipo: 'pdf' | 'doc' | 'xls' | 'otro';
  url: string;
  fechaSubida: Date;
  tamaño: number;
  hash: string;
}

export interface Plantilla {
  id: string;
  nombre: string;
  descripcion: string;
  campos: Campo[];
  fuente: string;
  activa: boolean;
}

export interface Campo {
  id: string;
  nombre: string;
  tipo: 'texto' | 'numero' | 'fecha' | 'lista' | 'booleano';
  requerido: boolean;
  valorPorDefecto?: any;
  opciones?: string[];
  expresionRegular?: string;
}
