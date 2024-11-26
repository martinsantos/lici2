from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime
import uvicorn
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:3003",
    "http://127.0.0.1:3003",
    "http://0.0.0.0:3003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las origenes durante desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Get request body
        body = await request.body()
        if body:
            logger.info(f"Body: {body.decode()}")
    except Exception as e:
        logger.error(f"Error reading request body: {str(e)}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: Status {response.status_code}")
        logger.info(f"Process time: {process_time:.2f}s")
        
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error interno del servidor: {str(e)}"}
        )

# Datos de ejemplo
LICITACIONES = {
    "1": {
        "id": "1",
        "titulo": "Construcción de Puente Peatonal",
        "descripcion": "Proyecto de construcción de puente peatonal en zona urbana con especificaciones técnicas de última generación",
        "fechaPublicacion": "2024-01-15",
        "fechaApertura": "2024-02-01",
        "numeroExpediente": "EXP-2024-001",
        "numeroLicitacion": "LIC-2024-001",
        "organismo": "Ministerio de Obras Públicas",
        "contacto": {
            "nombre": "Juan Pérez",
            "email": "juan.perez@obras.gob",
            "telefono": "+54 11 4567-8900"
        },
        "monto": 5000000,
        "presupuesto": 5000000,
        "moneda": "ARS",
        "estado": "Abierta",
        "categoria": "Infraestructura",
        "ubicacion": "Buenos Aires, Argentina",
        "plazo": "45 días",
        "requisitos": [
            "Inscripción en Registro de Constructores",
            "Experiencia mínima de 5 años",
            "Capacidad financiera demostrable"
        ],
        "garantia": {
            "tipo": "Póliza de Caución",
            "monto": "500000",
            "plazo": "12 meses"
        },
        "documentos": [
            {
                "id": "doc1",
                "nombre": "Pliego de Condiciones",
                "tipo": "PDF",
                "tamaño": "2.5 MB",
                "url": "/documentos/pliego.pdf"
            },
            {
                "id": "doc2",
                "nombre": "Especificaciones Técnicas",
                "tipo": "PDF",
                "tamaño": "1.8 MB",
                "url": "/documentos/especificaciones.pdf"
            }
        ],
        "idioma": "Español",
        "etapa": "Presentación de ofertas",
        "modalidad": "Licitación Pública",
        "area": "Infraestructura Urbana"
    },
    "2": {
        "id": "2",
        "titulo": "Mantenimiento de Parques",
        "descripcion": "Servicio integral de mantenimiento y mejora de áreas verdes municipales",
        "fechaPublicacion": "2024-01-20",
        "fechaApertura": "2024-02-15",
        "numeroExpediente": "EXP-2024-002",
        "numeroLicitacion": "LIC-2024-002",
        "organismo": "Secretaría de Espacios Verdes",
        "contacto": {
            "nombre": "María González",
            "email": "maria.gonzalez@espaciosverdes.gob",
            "telefono": "+54 11 4567-8901"
        },
        "monto": 2000000,
        "presupuesto": 2000000,
        "moneda": "ARS",
        "estado": "Abierta",
        "categoria": "Servicios",
        "ubicacion": "Buenos Aires, Argentina",
        "plazo": "12 meses",
        "requisitos": [
            "Registro de Proveedores del Estado",
            "Experiencia en mantenimiento de parques",
            "Personal capacitado"
        ],
        "garantia": {
            "tipo": "Seguro de Caución",
            "monto": "200000",
            "plazo": "14 meses"
        },
        "documentos": [
            {
                "id": "doc3",
                "nombre": "Pliego de Bases y Condiciones",
                "tipo": "PDF",
                "tamaño": "1.5 MB",
                "url": "/documentos/pliego_parques.pdf"
            }
        ],
        "idioma": "Español",
        "etapa": "Evaluación técnica",
        "modalidad": "Concurso Público",
        "area": "Mantenimiento y Servicios"
    },
    "3": {
        "id": "3",
        "titulo": "Renovación de Equipos Médicos",
        "descripcion": "Adquisición de equipamiento médico de última generación para hospital local",
        "fechaPublicacion": "2024-01-25",
        "fechaApertura": "2024-02-20",
        "numeroExpediente": "EXP-2024-003",
        "numeroLicitacion": "LIC-2024-003",
        "organismo": "Ministerio de Salud",
        "contacto": {
            "nombre": "Carlos Rodríguez",
            "email": "carlos.rodriguez@salud.gob",
            "telefono": "+54 11 4567-8902"
        },
        "monto": 8000000,
        "presupuesto": 8000000,
        "moneda": "ARS",
        "estado": "Cerrada",
        "categoria": "Equipamiento Médico",
        "ubicacion": "Buenos Aires, Argentina",
        "plazo": "60 días",
        "requisitos": [
            "Importador autorizado de equipos médicos",
            "Certificación ISO 13485",
            "Servicio técnico local"
        ],
        "garantia": {
            "tipo": "Garantía Bancaria",
            "monto": "800000",
            "plazo": "24 meses"
        },
        "documentos": [
            {
                "id": "doc4",
                "nombre": "Especificaciones Técnicas",
                "tipo": "PDF",
                "tamaño": "3.2 MB",
                "url": "/documentos/especificaciones_medicas.pdf"
            },
            {
                "id": "doc5",
                "nombre": "Formularios de Presentación",
                "tipo": "PDF",
                "tamaño": "1.1 MB",
                "url": "/documentos/formularios.pdf"
            }
        ],
        "idioma": "Español",
        "etapa": "Adjudicación",
        "modalidad": "Licitación Pública",
        "area": "Equipamiento Hospitalario"
    }
}

@app.get("/")
async def read_root():
    """Endpoint raíz que devuelve un mensaje de estado"""
    logger.info("Acceso a la ruta raíz")
    return {"status": "ok", "message": "API de Licitaciones activa"}

@app.get("/licitaciones")
async def get_licitaciones():
    """Endpoint para obtener todas las licitaciones"""
    logger.info("Obteniendo lista de licitaciones")
    try:
        return {"status": "ok", "data": LICITACIONES}
    except Exception as e:
        logger.error(f"Error al obtener licitaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener licitaciones")

@app.get("/licitaciones/{licitacion_id}")
async def get_licitacion(licitacion_id: str):
    """Endpoint para obtener una licitación específica"""
    logger.info(f"Buscando licitación con ID: {licitacion_id}")
    
    try:
        if licitacion_id not in LICITACIONES:
            logger.warning(f"Licitación no encontrada: {licitacion_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Licitación {licitacion_id} no encontrada"
            )
        
        licitacion = LICITACIONES[licitacion_id]
        logger.info(f"Licitación encontrada: {json.dumps(licitacion, ensure_ascii=False)}")
        return {"status": "ok", "data": licitacion}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.post("/licitaciones")
async def filter_licitaciones(
    filters: dict = Body(...)
):
    try:
        filtered_licitaciones = list(LICITACIONES.values()).copy()
        
        # Apply filters
        if filters.get("search"):
            search_term = filters["search"].lower()
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if search_term in l["titulo"].lower() or search_term in l["descripcion"].lower()
            ]
        
        if filters.get("estado"):
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if l["estado"] == filters["estado"]
            ]
        
        if filters.get("entidad"):
            entidad_term = filters["entidad"].lower()
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if entidad_term in l.get("organismo", "").lower()
            ]
        
        if filters.get("fechaDesde"):
            fecha_desde = datetime.fromisoformat(filters["fechaDesde"])
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if datetime.fromisoformat(l["fechaApertura"]) >= fecha_desde
            ]
        
        if filters.get("fechaHasta"):
            fecha_hasta = datetime.fromisoformat(filters["fechaHasta"])
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if datetime.fromisoformat(l["fechaApertura"]) <= fecha_hasta
            ]
        
        if filters.get("presupuestoMin"):
            presupuesto_min = float(filters["presupuestoMin"])
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if float(l["presupuesto"]) >= presupuesto_min
            ]
        
        if filters.get("presupuestoMax"):
            presupuesto_max = float(filters["presupuestoMax"])
            filtered_licitaciones = [
                l for l in filtered_licitaciones
                if float(l["presupuesto"]) <= presupuesto_max
            ]
        
        return {
            "status": "success",
            "data": filtered_licitaciones
        }
    except Exception as e:
        logger.error(f"Error filtering licitaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error filtering licitaciones: {str(e)}"
        )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Manejador global de errores 500"""
    logger.error(f"Error 500 en {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    logger.info("Iniciando servidor de Licitaciones...")
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
