import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Crear usuarios de ejemplo
  await prisma.user.createMany({
    data: [
      {
        email: 'admin@licitometro.com',
        name: 'Administrador',
        role: 'ADMIN'
      },
      {
        email: 'analista@licitometro.com',
        name: 'Analista',
        role: 'ANALYST'
      }
    ],
    skipDuplicates: true
  });

  // Crear modelos de ML de ejemplo
  await prisma.mLModel.createMany({
    data: [
      {
        name: 'Predicción de Licitaciones',
        version: '1.0.0',
        type: 'CLASIFICACION',
        accuracy: 0.85
      },
      {
        name: 'Estimación de Presupuesto',
        version: '1.0.0',
        type: 'REGRESION',
        accuracy: 0.75
      }
    ],
    skipDuplicates: true
  });

  // Crear licitaciones de ejemplo
  await prisma.licitacion.createMany({
    data: [
      {
        title: 'Licitación de Infraestructura Tecnológica',
        description: 'Proyecto para modernización de infraestructura de red',
        status: 'ABIERTA',
        category: 'TECNOLOGIA',
        budget: 5000000.00,
        publishedDate: new Date(),
        closingDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 días desde ahora
      },
      {
        title: 'Licitación de Servicios de Consultoría',
        description: 'Servicios de consultoría estratégica para transformación digital',
        status: 'PENDIENTE',
        category: 'CONSULTORIA',
        budget: 2500000.00,
        publishedDate: new Date(),
        closingDate: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000) // 45 días desde ahora
      }
    ],
    skipDuplicates: true
  });

  console.log('Datos de inicialización creados exitosamente');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
