# Licitometro 2.0

Sistema inteligente de monitoreo y análisis de licitaciones públicas con módulo RECON integrado.

## Características Principales

- Frontend construido con Astro y React
- Diseño responsive y accesible (WCAG 2.1)
- Integración con FastAPI backend
- Sistema de plantillas para scraping configurable
- Análisis de documentos con Documind
- Búsqueda avanzada con Elasticsearch

## Requisitos Previos

- Node.js 18+
- npm 8+
- Python 3.11+
- PostgreSQL 14+
- Elasticsearch 8+
- Redis 7+
- MinIO

## Instalación

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd licitometro
```

2. Instalar dependencias:
```bash
npm install
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
```

4. Iniciar el servidor de desarrollo:
```bash
npm run dev
```

## Estructura del Proyecto

```
licitometro/
├── src/
│   ├── components/    # Componentes React reutilizables
│   ├── layouts/       # Layouts de Astro
│   ├── pages/         # Páginas de la aplicación
│   ├── styles/        # Estilos globales y utilidades
│   ├── utils/         # Funciones de utilidad
│   ├── store/         # Estado global de la aplicación
│   └── types/         # Definiciones de TypeScript
├── public/           # Archivos estáticos
└── backend/          # Servicios de backend (en otro repositorio)
```

## Scripts Disponibles

- `npm run dev`: Inicia el servidor de desarrollo
- `npm run build`: Construye la aplicación para producción
- `npm run preview`: Vista previa de la build de producción
- `npm run lint`: Ejecuta el linter
- `npm run test`: Ejecuta las pruebas

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.
