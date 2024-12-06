import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function cleanDuplicateLicitaciones() {
  try {
    console.log('Iniciando limpieza de licitaciones duplicadas...');

    // Obtener todas las licitaciones ordenadas por fecha de creación (más recientes primero)
    const licitaciones = await prisma.licitacion.findMany({
      orderBy: {
        createdAt: 'desc'
      }
    });

    console.log(`Total de licitaciones encontradas: ${licitaciones.length}`);

    // Agrupar por título para identificar duplicados
    const licitacionesPorTitulo = new Map();
    const duplicadasParaBorrar = [];

    licitaciones.forEach(licitacion => {
      if (!licitacionesPorTitulo.has(licitacion.titulo)) {
        // Si es la primera vez que vemos este título, guardamos esta versión
        licitacionesPorTitulo.set(licitacion.titulo, licitacion);
      } else {
        // Si ya existe una con este título, esta es una duplicada (más antigua)
        duplicadasParaBorrar.push(licitacion.id);
      }
    });

    console.log(`Encontradas ${duplicadasParaBorrar.length} licitaciones duplicadas`);

    if (duplicadasParaBorrar.length > 0) {
      // Eliminar las licitaciones duplicadas
      const resultado = await prisma.licitacion.deleteMany({
        where: {
          id: {
            in: duplicadasParaBorrar
          }
        }
      });

      console.log(`Eliminadas ${resultado.count} licitaciones duplicadas`);
    } else {
      console.log('No se encontraron licitaciones duplicadas');
    }

  } catch (error) {
    console.error('Error al limpiar duplicados:', error);
  } finally {
    await prisma.$disconnect();
  }
}

// Ejecutar la limpieza
cleanDuplicateLicitaciones();
