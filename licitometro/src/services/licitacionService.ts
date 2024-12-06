import prisma from '../lib/prisma';
import type { 
  Licitacion, 
  Garantia, 
  Contacto, 
  Documento, 
  Requisito,
  Participante,
  Prisma
} from '@prisma/client';

type LicitacionWithRelations = Licitacion & {
  garantia?: Garantia;
  contacto?: Contacto;
  documentos?: Documento[];
  requisitos?: Requisito[];
  participantes?: Participante[];
};

type CreateLicitacionInput = Prisma.LicitacionCreateInput;
type UpdateLicitacionInput = Prisma.LicitacionUpdateInput;

export class LicitacionService {
  // Obtener todas las licitaciones con sus relaciones
  static async getAllLicitaciones(): Promise<LicitacionWithRelations[]> {
    try {
      return await prisma.licitacion.findMany({
        where: {
          isActive: true
        },
        include: {
          garantia: true,
          contacto: true,
          documentos: true,
          requisitos: true
        },
        orderBy: {
          fechaPublicacion: 'desc'
        }
      });
    } catch (error) {
      console.error('Error al obtener licitaciones:', error);
      throw new Error('Error al obtener las licitaciones');
    }
  }

  // Obtener una licitación por ID
  static async getLicitacionById(id: string): Promise<LicitacionWithRelations | null> {
    try {
      return await prisma.licitacion.findUnique({
        where: { id },
        include: {
          garantia: true,
          contacto: true,
          documentos: true,
          requisitos: true,
          participantes: true
        }
      });
    } catch (error) {
      console.error(`Error al obtener licitación ${id}:`, error);
      throw new Error(`Error al obtener la licitación ${id}`);
    }
  }

  // Crear una nueva licitación
  static async createLicitacion(data: CreateLicitacionInput): Promise<LicitacionWithRelations> {
    try {
      return await prisma.licitacion.create({
        data,
        include: {
          garantia: true,
          contacto: true,
          documentos: true,
          requisitos: true
        }
      });
    } catch (error) {
      console.error('Error al crear licitación:', error);
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2002') {
          throw new Error('Ya existe una licitación con ese número');
        }
      }
      throw new Error('Error al crear la licitación');
    }
  }

  // Actualizar una licitación
  static async updateLicitacion(
    id: string, 
    data: UpdateLicitacionInput
  ): Promise<LicitacionWithRelations> {
    try {
      return await prisma.licitacion.update({
        where: { id },
        data,
        include: {
          garantia: true,
          contacto: true,
          documentos: true,
          requisitos: true
        }
      });
    } catch (error) {
      console.error(`Error al actualizar licitación ${id}:`, error);
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2025') {
          throw new Error('Licitación no encontrada');
        }
      }
      throw new Error(`Error al actualizar la licitación ${id}`);
    }
  }

  // Eliminar una licitación (soft delete)
  static async deleteLicitacion(id: string): Promise<Licitacion> {
    try {
      return await prisma.licitacion.update({
        where: { id },
        data: {
          isActive: false
        }
      });
    } catch (error) {
      console.error(`Error al eliminar licitación ${id}:`, error);
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2025') {
          throw new Error('Licitación no encontrada');
        }
      }
      throw new Error(`Error al eliminar la licitación ${id}`);
    }
  }

  // Búsqueda avanzada de licitaciones
  static async searchLicitaciones(params: {
    query?: string;
    estado?: string;
    organismo?: string;
    fechaDesde?: Date;
    fechaHasta?: Date;
    presupuestoMin?: number;
    presupuestoMax?: number;
  }): Promise<LicitacionWithRelations[]> {
    try {
      const {
        query,
        estado,
        organismo,
        fechaDesde,
        fechaHasta,
        presupuestoMin,
        presupuestoMax
      } = params;

      const where: Prisma.LicitacionWhereInput = {
        isActive: true,
        AND: [
          // Búsqueda por texto en título y descripción
          query ? {
            OR: [
              { titulo: { contains: query, mode: 'insensitive' } },
              { descripcion: { contains: query, mode: 'insensitive' } }
            ]
          } : {},
          // Filtros adicionales
          estado ? { estado: estado as any } : {},
          organismo ? { organismo: { contains: organismo, mode: 'insensitive' } } : {},
          // Rango de fechas
          fechaDesde || fechaHasta ? {
            fechaPublicacion: {
              gte: fechaDesde,
              lte: fechaHasta
            }
          } : {},
          // Rango de presupuesto
          presupuestoMin || presupuestoMax ? {
            presupuesto: {
              gte: presupuestoMin,
              lte: presupuestoMax
            }
          } : {}
        ]
      };

      return await prisma.licitacion.findMany({
        where,
        include: {
          garantia: true,
          contacto: true,
          documentos: true,
          requisitos: true
        },
        orderBy: {
          fechaPublicacion: 'desc'
        }
      });
    } catch (error) {
      console.error('Error en la búsqueda de licitaciones:', error);
      throw new Error('Error al buscar licitaciones');
    }
  }

  // Validar una licitación
  static validateLicitacion(data: Partial<CreateLicitacionInput>): boolean {
    const requiredFields: (keyof Licitacion)[] = [
      'titulo',
      'descripcion',
      'estado',
      'organismo',
      'presupuesto',
      'moneda',
      'fechaPublicacion',
      'fechaApertura'
    ];

    return requiredFields.every(field => {
      const value = data[field];
      return value !== undefined && value !== null && value !== '';
    });
  }
}
