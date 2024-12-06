from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar rutas
from routes import include_router

# Crear aplicación FastAPI
app = FastAPI(
    title="Licitometro RECON API",
    description="API para gestión de plantillas de scraping y extracción de datos",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de RECON
include_router(app)

# Endpoint de salud
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Configuración para ejecución directa
def start_server():
    """
    Iniciar el servidor de desarrollo
    """
    uvicorn.run(
        "main:app", 
        host=os.getenv('RECON_API_HOST', 'localhost'), 
        port=int(os.getenv('RECON_API_PORT', 3004)),
        reload=True
    )

if __name__ == "__main__":
    start_server()
