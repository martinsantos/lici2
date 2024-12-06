# Licitometro API

API REST para la gestión de licitaciones públicas.

## Características

- Gestión de usuarios con roles (admin, manager, user)
- CRUD completo de licitaciones
- Búsqueda y filtrado avanzado de licitaciones
- Autenticación JWT
- Documentación OpenAPI (Swagger)

## Requisitos

- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL/SQLite

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd licitometro-api
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con las configuraciones necesarias
```

## Ejecución

1. Iniciar el servidor de desarrollo:
```bash
uvicorn app.main:app --reload
```

2. Acceder a la documentación:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/       # Endpoints de la API
│   ├── core/               # Configuraciones centrales
│   ├── database/           # Modelos y operaciones de BD
│   ├── models/            # Modelos Pydantic
│   └── services/          # Lógica de negocio
├── tests/                 # Tests
└── requirements.txt       # Dependencias
```

## API Endpoints

### Autenticación
- POST `/api/v1/token` - Obtener token de acceso

### Usuarios
- POST `/api/v1/users` - Crear usuario
- GET `/api/v1/users` - Listar usuarios
- GET `/api/v1/users/{id}` - Obtener usuario
- PUT `/api/v1/users/{id}` - Actualizar usuario
- DELETE `/api/v1/users/{id}` - Eliminar usuario

### Licitaciones
- POST `/api/v1/tenders` - Crear licitación
- GET `/api/v1/tenders` - Listar licitaciones
- GET `/api/v1/tenders/{id}` - Obtener licitación
- PUT `/api/v1/tenders/{id}` - Actualizar licitación
- DELETE `/api/v1/tenders/{id}` - Eliminar licitación
- PATCH `/api/v1/tenders/{id}/status` - Actualizar estado

## Tests

Ejecutar tests:
```bash
pytest
```

## Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

MIT License
