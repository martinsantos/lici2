import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';
import { Server } from 'http';
import { AddressInfo } from 'net';

// Configuración de variables de entorno
dotenv.config();

// Inicializar Prisma Client
const prisma = new PrismaClient();

// Crear aplicación Express
const app = express();

// Configuración de CORS más permisiva para desarrollo
const corsOptions = {
  origin: [
    'http://localhost:5173',  // Vite dev server
    'http://127.0.0.1:5173',
    'http://localhost:3000',  // Posibles puertos de frontend
    'http://127.0.0.1:3000'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
};

// Middleware
app.use(cors(corsOptions));
app.use(express.json());

// Rutas de ejemplo
app.get('/', (req, res) => {
  res.json({ 
    message: 'Bienvenido a Licitometro ML Platform', 
    status: 'OK',
    endpoints: [
      '/licitaciones',
      // Añadir más endpoints aquí
    ]
  });
});

// Ruta para obtener licitaciones
app.get('/licitaciones', async (req, res) => {
  try {
    const licitaciones = await prisma.licitacion.findMany({
      take: 50, // Limitar a 50 resultados inicialmente
      orderBy: {
        createdAt: 'desc' // Cambiar a un campo que exista en el modelo
      }
    });
    res.json(licitaciones);
  } catch (error) {
    console.error('Error al obtener licitaciones:', error);
    res.status(500).json({ 
      error: 'Error al obtener licitaciones',
      details: error instanceof Error ? error.message : 'Error desconocido'
    });
  }
});

// Rutas de admin
app.get('/admin', (req, res) => {
  res.json({
    message: 'Panel de Administración de Licitometro',
    sections: [
      'usuarios',
      'licitaciones',
      'modelos-ml',
      'configuraciones'
    ]
  });
});

app.get('/admin/usuarios', async (req, res) => {
  try {
    // Simular datos de usuarios (sustituir con consulta real)
    const usuarios = [
      { id: '1', nombre: 'Admin Principal', rol: 'superadmin' },
      { id: '2', nombre: 'Analista', rol: 'analista' }
    ];
    res.json(usuarios);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener usuarios' });
  }
});

app.get('/admin/licitaciones', async (req, res) => {
  try {
    const licitaciones = await prisma.licitacion.findMany({
      take: 100,
      orderBy: { createdAt: 'desc' }
    });
    res.json(licitaciones);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener licitaciones' });
  }
});

// Convertir PORT a número, usar 0 para puerto aleatorio
const PORT = Number(process.env.PORT || 0);

// Iniciar servidor
const server: Server = app.listen(PORT, '0.0.0.0', () => {
  const address = server.address();
  const port = typeof address === 'string' ? address : 
    (address as AddressInfo).port;
  
  console.log(`🚀 Servidor Licitometro corriendo en puerto ${port}`);
  console.log(`Ambiente: ${process.env.NODE_ENV || 'development'}`);
});

// Manejo de cierre de aplicación
process.on('SIGINT', async () => {
  await prisma.$disconnect();
  server.close();
  process.exit(0);
});
