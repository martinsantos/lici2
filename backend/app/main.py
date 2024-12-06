from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, users, tenders
from app.database.base import Base, engine

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Licitometro API",
    description="""
    API para la gestión de licitaciones públicas. 
    
    Esta API permite:
    * Gestionar usuarios y autenticación
    * Crear y administrar licitaciones
    * Buscar y filtrar licitaciones por diversos criterios
    * Administrar documentos y requisitos de licitaciones
    """,
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "desarrollo@licitometro.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Autenticación"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["Usuarios"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    tenders.router,
    prefix="/api/v1",
    tags=["Licitaciones"],
    responses={404: {"description": "Not found"}},
)

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz que proporciona información básica sobre la API.
    """
    return {
        "message": "Bienvenido a la API de Licitometro",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
