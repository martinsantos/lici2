from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.api_config import api_config
from core.database import Base, engine
from recon_service.recon_routes import router as recon_router
from licitaciones.routes import router as licitaciones_router
from document_service.routes import router as document_router
from search_service.routes import router as search_router
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Licitometro API",
    version=api_config.API_VERSION,
    docs_url=f"{api_config.BASE_PATH}/docs",
    redoc_url=f"{api_config.BASE_PATH}/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(recon_router, prefix=api_config.BASE_PATH)
app.include_router(licitaciones_router, prefix=api_config.BASE_PATH)
app.include_router(document_router, prefix=api_config.BASE_PATH)
app.include_router(search_router, prefix=api_config.BASE_PATH)

# Modelo Pydantic para la validación de datos
class LicitacionBase(BaseModel):
    titulo: str
    descripcion: str
    fechaPublicacion: datetime
    fechaApertura: Optional[datetime] = None
    numeroExpediente: Optional[str] = None
    numeroLicitacion: Optional[str] = None
    organismo: Optional[str] = None
    contacto: Optional[str] = None
    monto: Optional[float] = 0
    estado: Optional[str] = "Pendiente"
    categoria: Optional[str] = None
    ubicacion: Optional[str] = None
    plazo: Optional[str] = None
    requisitos: List[str] = []
    garantia: Optional[str] = None
    documentos: List[str] = []
    presupuesto: Optional[float] = 0
    moneda: Optional[str] = "ARS"
    idioma: Optional[str] = "es"
    etapa: Optional[str] = None
    modalidad: Optional[str] = None
    area: Optional[str] = None

class LicitacionCreate(LicitacionBase):
    pass

class Licitacion(LicitacionBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# Inicializar cliente SQLAlchemy
Session = sessionmaker(bind=engine)

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

@app.get("/api/v1/licitaciones", response_model=List[Licitacion])
async def get_licitaciones():
    try:
        session = Session()
        licitaciones = session.query(Licitacion).order_by(Licitacion.fechaPublicacion.desc()).all()
        return licitaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/licitaciones", response_model=Licitacion, status_code=201)
async def create_licitacion(licitacion: LicitacionCreate):
    try:
        session = Session()
        nueva_licitacion = Licitacion(
            titulo=licitacion.titulo,
            descripcion=licitacion.descripcion,
            fechaPublicacion=licitacion.fechaPublicacion,
            fechaApertura=licitacion.fechaApertura,
            numeroExpediente=licitacion.numeroExpediente,
            numeroLicitacion=licitacion.numeroLicitacion,
            organismo=licitacion.organismo,
            contacto=licitacion.contacto,
            monto=licitacion.monto,
            estado=licitacion.estado,
            categoria=licitacion.categoria,
            ubicacion=licitacion.ubicacion,
            plazo=licitacion.plazo,
            requisitos=licitacion.requisitos,
            garantia=licitacion.garantia,
            documentos=licitacion.documentos,
            presupuesto=licitacion.presupuesto,
            moneda=licitacion.moneda,
            idioma=licitacion.idioma,
            etapa=licitacion.etapa,
            modalidad=licitacion.modalidad,
            area=licitacion.area,
        )
        session.add(nueva_licitacion)
        session.commit()
        return nueva_licitacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/licitaciones/{licitacion_id}", response_model=Licitacion)
async def get_licitacion(licitacion_id: int):
    try:
        session = Session()
        licitacion = session.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
        if not licitacion:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        return licitacion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
