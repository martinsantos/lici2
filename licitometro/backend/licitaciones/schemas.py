from pydantic import BaseModel, ConfigDict, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class ContactoBase(BaseModel):
    nombre: str
    email: str
    telefono: str

class GarantiaBase(BaseModel):
    tipo: str
    monto: str
    plazo: str

class DocumentoBase(BaseModel):
    id: str
    nombre: str
    tipo: str
    tamaño: str
    url: str

class ExtractoBase(BaseModel):
    id: str
    texto: str
    tipo: str
    fecha_extraccion: datetime
    fuente: str

class LicitacionBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_publicacion: datetime
    fecha_apertura: Optional[datetime] = None
    numero_expediente: Optional[str] = None
    numero_licitacion: Optional[str] = None
    organismo: str
    contacto: Optional[Dict[str, Any]] = None
    monto: Optional[float] = None
    presupuesto: Optional[float] = None
    moneda: Optional[str] = None
    estado: str
    categoria: Optional[str] = None
    ubicacion: Optional[str] = None
    plazo: Optional[str] = None
    requisitos: Optional[List[str]] = None
    garantia: Optional[Dict[str, Any]] = None
    documentos: Optional[List[Dict[str, Any]]] = None
    extractos: Optional[List[Dict[str, Any]]] = None
    idioma: Optional[str] = None
    etapa: Optional[str] = None
    modalidad: Optional[str] = None
    area: Optional[str] = None

    @validator('fecha_publicacion', 'fecha_apertura', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                # Intentar parsear diferentes formatos
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    try:
                        # Manejar formatos con zona horaria
                        return datetime.strptime(v.split(" GMT")[0], "%a %b %d %Y %H:%M:%S")
                    except ValueError:
                        raise ValueError(f"No se pudo parsear la fecha: {v}")
        return v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
    )

class LicitacionCreate(LicitacionBase):
    pass

class Licitacion(LicitacionBase):
    id: str
    codigo: str
    fuente: str
    url_fuente: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
    )

class LicitacionResponse(Licitacion, LicitacionBase):
    """
    Schema para respuestas de licitaciones, combina Licitacion y LicitacionBase
    """
    documentos: Optional[List[DocumentoBase]] = None
    extractos: Optional[List[ExtractoBase]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
    )
