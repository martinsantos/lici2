from sqlalchemy import Column, String, DateTime, Float, JSON, Boolean
from sqlalchemy.sql import func
from core.database import Base

class Licitacion(Base):
    __tablename__ = "licitaciones"

    id = Column(String, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)
    titulo = Column(String)
    descripcion = Column(String, nullable=True)
    fecha_publicacion = Column(DateTime)
    fecha_apertura = Column(DateTime, nullable=True)
    numero_expediente = Column(String, nullable=True)
    numero_licitacion = Column(String, nullable=True)
    organismo = Column(String)
    contacto = Column(JSON, nullable=True)
    monto = Column(Float, nullable=True)
    presupuesto = Column(Float, nullable=True)
    moneda = Column(String, nullable=True)
    estado = Column(String)
    categoria = Column(String, nullable=True)
    ubicacion = Column(String, nullable=True)
    plazo = Column(String, nullable=True)
    requisitos = Column(JSON, nullable=True)
    garantia = Column(JSON, nullable=True)
    documentos = Column(JSON, nullable=True)
    extractos = Column(JSON, nullable=True)
    idioma = Column(String, nullable=True)
    etapa = Column(String, nullable=True)
    modalidad = Column(String, nullable=True)
    area = Column(String, nullable=True)
    fuente = Column(String)
    url_fuente = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Template(Base):
    __tablename__ = "templates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    url = Column(String)
    config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
