import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Limpiar la base de datos
  await prisma.licitacion.deleteMany();

  // Crear algunas licitaciones de prueba
  const licitaciones = [
    {
      titulo: 'Construcción de Escuela Primaria',
      descripcion: 'Proyecto de construcción de una nueva escuela primaria en el barrio San Martín',
      fechaPublicacion: new Date('2024-01-15'),
      fechaApertura: new Date('2024-02-15'),
      numeroExpediente: 'EXP-2024-001',
      numeroLicitacion: 'LIC-2024-001',
      organismo: 'Ministerio de Educación',
      contacto: 'Juan Pérez - juan.perez@educacion.gob.ar',
      monto: 50000000,
      estado: 'Pendiente',
      categoria: 'Infraestructura Educativa',
      ubicacion: 'Buenos Aires',
      plazo: '12 meses',
      requisitos: ['Experiencia en construcción de escuelas', 'Certificación ISO 9001'],
      garantia: 'Póliza de caución por el 10% del monto total',
      documentos: ['pliego.pdf', 'planos.dwg'],
      presupuesto: 50000000,
      moneda: 'ARS',
      idioma: 'es',
      etapa: 'Publicación',
      modalidad: 'Licitación Pública',
      area: 'Construcción',
    },
    {
      titulo: 'Provisión de Equipamiento Informático',
      descripcion: 'Adquisición de computadoras y equipamiento informático para oficinas gubernamentales',
      fechaPublicacion: new Date('2024-01-10'),
      fechaApertura: new Date('2024-02-10'),
      numeroExpediente: 'EXP-2024-002',
      numeroLicitacion: 'LIC-2024-002',
      organismo: 'Ministerio de Modernización',
      contacto: 'María González - maria.gonzalez@modernizacion.gob.ar',
      monto: 25000000,
      estado: 'Pendiente',
      categoria: 'Tecnología',
      ubicacion: 'CABA',
      plazo: '3 meses',
      requisitos: ['Distribuidor autorizado', 'Servicio técnico oficial'],
      garantia: 'Póliza de caución por el 5% del monto total',
      documentos: ['especificaciones.pdf'],
      presupuesto: 25000000,
      moneda: 'ARS',
      idioma: 'es',
      etapa: 'Publicación',
      modalidad: 'Licitación Pública',
      area: 'Tecnología',
    },
  ];

  for (const licitacion of licitaciones) {
    await prisma.licitacion.create({
      data: licitacion,
    });
  }

  console.log('Base de datos poblada con datos de prueba');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
