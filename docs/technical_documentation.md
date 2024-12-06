# Documentación Técnica - Licitometro 2.0

## Arquitectura General

### Frontend (ASTRO + React)
- **Estructura**
  - `/src/pages`: Páginas estáticas generadas con ASTRO
  - `/src/components`: Componentes React reutilizables
  - `/src/layouts`: Layouts compartidos
  - `/src/styles`: Estilos globales y temas

### Backend (FastAPI)
- **Módulos Principales**
  - `app/recon`: Sistema de reconocimiento y scraping
  - `app/search`: Servicio de búsqueda con Elasticsearch
  - `app/notifications`: Sistema de notificaciones

## Módulos Principales

### 1. Módulo RECON
- **Componentes**
  - `enhanced_coordinator.py`: Coordinador principal de tareas
  - `task_manager.py`: Gestión de tareas asíncronas
  - `document_analyzer.py`: Análisis de documentos
  - `monitoring.py`: Sistema de monitoreo

### 2. Servicio de Búsqueda
- **Características**
  - Búsqueda full-text en español
  - Filtrado por múltiples campos
  - Geolocalización de resultados
  - Ordenamiento por relevancia y fecha

### 3. Sistema de Notificaciones
- **Funcionalidades**
  - Notificaciones en tiempo real
  - Envío de emails
  - Persistencia en Redis
  - Estado de lectura

## Guías de Desarrollo

### Configuración del Entorno
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Variables de entorno:
   ```env
   ELASTICSEARCH_HOSTS=["http://localhost:9200"]
   REDIS_URL=redis://localhost:6379
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   ```

### Desarrollo Frontend
1. Ejecutar en modo desarrollo:
   ```bash
   npm run dev
   ```

2. Construir para producción:
   ```bash
   npm run build
   ```

### Desarrollo Backend
1. Ejecutar servidor de desarrollo:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Ejecutar tests:
   ```bash
   pytest tests/
   ```

## APIs y Endpoints

### API de Búsqueda
```python
GET /api/search
Parameters:
  - query: str
  - filters: Dict
  - from_: int
  - size: int
```

### API de Notificaciones
```python
POST /api/notifications
Body:
  - user_id: str
  - notification: Dict
```

## Monitoreo y Métricas

### Prometheus Metrics
- `recon_tasks_total`: Total de tareas procesadas
- `recon_tasks_success`: Tareas exitosas
- `recon_tasks_failed`: Tareas fallidas
- `search_latency`: Latencia de búsquedas

### Logs
- Formato: JSON
- Niveles: INFO, WARNING, ERROR
- Rotación: Diaria

## Seguridad

### Autenticación
- JWT para autenticación de API
- Tokens de refresh
- Rate limiting por IP/usuario

### Autorización
- RBAC (Role-Based Access Control)
- Scopes por endpoint
- Auditoría de accesos

## Despliegue

### Docker
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    
  elasticsearch:
    image: elasticsearch:8.x
    ports:
      - "9200:9200"
    
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

### CI/CD
- GitHub Actions para CI
- Despliegue automático a staging
- Tests automáticos
- Análisis de código estático

## Mantenimiento

### Backups
- Elasticsearch: Snapshots diarios
- PostgreSQL: Dumps incrementales
- Redis: RDB + AOF

### Monitoreo
- Grafana para visualización
- Alertas configuradas
- Métricas de negocio
