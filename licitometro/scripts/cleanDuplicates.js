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

    // Agrupar por título y número de licitación para identificar duplicados
    const licitacionesPorIdentificador = new Map();
    const duplicadasParaBorrar = [];

    licitaciones.forEach(licitacion => {
      // Crear un identificador único combinando título y número de licitación
      const identificador = `${licitacion.titulo}-${licitacion.numeroLicitacion}`;
      
      if (!licitacionesPorIdentificador.has(identificador)) {
        // Si es la primera vez que vemos esta combinación, guardamos esta versión
        licitacionesPorIdentificador.set(identificador, licitacion);
      } else {
        // Si ya existe una con esta combinación, esta es una duplicada (más antigua)
        duplicadasParaBorrar.push(licitacion.id);
      }
    });

    console.log(`Encontradas ${duplicadasParaBorrar.length} licitaciones duplicadas`);

    if (duplicadasParaBorrar.length > 0) {
      // Mostrar las licitaciones que se van a eliminar
      console.log('\nLicitaciones a eliminar:');
      duplicadasParaBorrar.forEach(id => {
        const licitacion = licitaciones.find(l => l.id === id);
        console.log(`- ${licitacion.titulo} (ID: ${licitacion.id}, Número: ${licitacion.numeroLicitacion})`);
      });

      // Eliminar las licitaciones duplicadas
      const resultado = await prisma.licitacion.deleteMany({
        where: {
          id: {
            in: duplicadasParaBorrar
          }
        }
      });

      console.log(`\nEliminadas ${resultado.count} licitaciones duplicadas`);
      
      // Mostrar las licitaciones que se mantuvieron
      console.log('\nLicitaciones mantenidas:');
      for (const [identificador, licitacion] of licitacionesPorIdentificador) {
        console.log(`- ${licitacion.titulo} (ID: ${licitacion.id}, Número: ${licitacion.numeroLicitacion})`);
      }
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
