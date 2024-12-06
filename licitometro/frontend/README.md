# Licitometro Frontend

## Descripción
Frontend para la aplicación Licitometro, desarrollado con React, Vite y TypeScript.

## Requisitos Previos
- Node.js (v18 o superior)
- npm (v9 o superior)

## Instalación

1. Clonar el repositorio
```bash
git clone [URL_DEL_REPOSITORIO]
cd licitometro/frontend
```

2. Instalar dependencias
```bash
npm install
```

3. Configurar variables de entorno
- Copiar `.env.example` a `.env`
- Ajustar las configuraciones según sea necesario

## Scripts Disponibles

- `npm run dev`: Iniciar servidor de desarrollo
- `npm run build`: Compilar para producción
- `npm run preview`: Vista previa de la compilación de producción
- `npm run test`: Ejecutar pruebas
- `npm run test:watch`: Ejecutar pruebas en modo watch
- `npm run test:coverage`: Generar reporte de cobertura de pruebas

## Configuración de Entorno

### Variables de Entorno
- `VITE_API_BASE_URL`: URL base del backend
- `VITE_API_TIMEOUT`: Timeout de solicitudes API
- `VITE_MAX_FILE_UPLOAD_SIZE`: Tamaño máximo de archivos
- `VITE_ALLOWED_FILE_TYPES`: Tipos de archivo permitidos

## Estructura del Proyecto
```
frontend/
├── public/
├── src/
│   ├── components/
│   ├── config/
│   ├── services/
│   ├── test/
│   ├── types/
│   └── utils/
├── .env
├── vite.config.ts
└── tsconfig.json
```

## Desarrollo

### Buenas Prácticas
- Usar TypeScript estricto
- Escribir pruebas unitarias
- Seguir guías de estilo de React

## Problemas Comunes
- Asegurarse de que el backend esté corriendo
- Verificar configuraciones de variables de entorno

## Licencia
[Especificar Licencia]
