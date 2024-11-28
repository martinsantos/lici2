from sqlalchemy import Column, String, DateTime, Float, JSON, Text
from sqlalchemy.sql import func
from core.database import Base

class Licitacion(Base):
    __tablename__ = "licitaciones"

    id = Column(String, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)  # Código único de la licitación
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    fecha_publicacion = Column(DateTime, server_default=func.now())
    fecha_apertura = Column(DateTime)
    numero_expediente = Column(String)
    numero_licitacion = Column(String)
    organismo = Column(String)
    contacto = Column(JSON)  # {nombre, email, telefono}
    monto = Column(Float)
    presupuesto = Column(Float)
    moneda = Column(String)
    estado = Column(String)
    categoria = Column(String)
    ubicacion = Column(String)
    plazo = Column(String)
    requisitos = Column(JSON)  # Array de strings
    garantia = Column(JSON)  # {tipo, monto, plazo}
    documentos = Column(JSON)  # Array de {id, nombre, tipo, tamaño, url}
    extractos = Column(JSON)  # Array de {texto, fecha, fuente}
    idioma = Column(String)
    etapa = Column(String)
    modalidad = Column(String)
    area = Column(String)
    fuente = Column(String, nullable=False)  # Nombre del portal fuente
    url_fuente = Column(String, nullable=False)  # URL del portal fuente
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
