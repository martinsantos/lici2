import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Checking licitaciones in database...');
  
  const licitaciones = await prisma.licitacion.findMany({
    orderBy: {
      fechaPublicacion: 'desc'
    }
  });

  console.log('Found licitaciones:', licitaciones.length);
  console.log('Licitaciones:', JSON.stringify(licitaciones, null, 2));
}

main()
  .catch(console.error)
  .finally(async () => {
    await prisma.$disconnect();
  });
