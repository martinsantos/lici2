from sqlalchemy import Column, String, DateTime, Float, Text, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib
import os

from ..logging_config import get_logger
from ....core.database import engine, Base, get_db

class Licitacion(Base):
    """
    SQLAlchemy model for Licitaciones
    """
    __tablename__ = 'licitaciones'

    id = Column(String, primary_key=True)
    codigo = Column(String)
    titulo = Column(String)
    organismo = Column(String)
    url_fuente = Column(String)
    fecha_publicacion = Column(DateTime)
    estado = Column(String, default='En Proceso')
    monto = Column(Float, default=0.0)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    datos_extra = Column(Text)

class LicitacionesPersistencia:
    """
    Class to manage Licitaciones persistence using SQLAlchemy and PostgreSQL
    """
    def __init__(self):
        """
        Initialize database connection
        """
        self.logger = get_logger(self.__class__.__name__)
        self.SessionLocal = sessionmaker(bind=engine)

    def _generar_id_unico(self, licitacion: Dict) -> str:
        """
        Generate unique ID for a licitacion based on its data
        
        Args:
            licitacion (Dict): Licitacion dictionary
        
        Returns:
            str: Unique MD5 hash
        """
        # Fields to generate unique ID
        campos_id = [
            licitacion.get('titulo', ''),
            licitacion.get('organismo', ''),
            licitacion.get('url_fuente', ''),
            str(licitacion.get('fecha_publicacion', ''))
        ]
        
        # Generate hash
        hash_input = '|'.join(campos_id).encode('utf-8')
        return hashlib.md5(hash_input).hexdigest()

    def guardar_licitacion(self, licitacion: Dict) -> bool:
        """
        Save a licitacion to the database
        
        Args:
            licitacion (Dict): Licitacion dictionary to save
        
        Returns:
            bool: True if saved, False on error
        """
        try:
            # Generate unique ID
            licitacion_id = self._generar_id_unico(licitacion)
            
            # Convert date to datetime
            fecha_publicacion = licitacion.get('fecha_publicacion', datetime.now())
            if not isinstance(fecha_publicacion, datetime):
                fecha_publicacion = datetime.fromisoformat(fecha_publicacion)
            
            # Prepare extra data
            datos_extra = {
                k: v for k, v in licitacion.items() 
                if k not in ['codigo', 'titulo', 'organismo', 'url_fuente', 'fecha_publicacion', 'estado', 'monto']
            }

            # Create session
            session = next(get_db())
            
            # Create Licitacion object
            db_licitacion = Licitacion(
                id=licitacion_id,
                codigo=licitacion.get('codigo'),
                titulo=licitacion.get('titulo'),
                organismo=licitacion.get('organismo'),
                url_fuente=licitacion.get('url_fuente'),
                fecha_publicacion=fecha_publicacion,
                estado=licitacion.get('estado', 'En Proceso'),
                monto=licitacion.get('monto', 0.0),
                datos_extra=json.dumps(datos_extra)
            )

            # Add and commit
            session.merge(db_licitacion)
            session.commit()
            
            return True
        
        except SQLAlchemyError as e:
            self.logger.error(f"Error saving licitacion: {e}")
            return False
        finally:
            session.close()

    def guardar_licitaciones_batch(self, licitaciones: List[Dict]) -> Dict:
        """
        Save multiple licitaciones in a single batch
        
        Args:
            licitaciones (List[Dict]): List of licitaciones to save
        
        Returns:
            Dict: Saving statistics
        """
        resultados = {
            'total': len(licitaciones),
            'guardadas': 0,
            'errores': 0
        }

        for licitacion in licitaciones:
            if self.guardar_licitacion(licitacion):
                resultados['guardadas'] += 1
            else:
                resultados['errores'] += 1

        self.logger.info(
            f"Saved {resultados['guardadas']} of {resultados['total']} licitaciones"
        )

        return resultados

    def buscar_licitaciones(
        self, 
        titulo: str = None, 
        organismo: str = None, 
        estado: str = None,
        fecha_desde: datetime = None,
        fecha_hasta: datetime = None
    ) -> List[Dict]:
        """
        Search for licitaciones with filters
        
        Args:
            titulo (str, optional): Filter by title
            organismo (str, optional): Filter by organization
            estado (str, optional): Filter by state
            fecha_desde (datetime, optional): Publication date from
            fecha_hasta (datetime, optional): Publication date to
        
        Returns:
            List[Dict]: List of licitaciones matching the filters
        """
        try:
            session = next(get_db())
            
            # Build base query
            query = session.query(Licitacion)
            
            # Add filters
            if titulo:
                query = query.filter(Licitacion.titulo.ilike(f"%{titulo}%"))
            
            if organismo:
                query = query.filter(Licitacion.organismo.ilike(f"%{organismo}%"))
            
            if estado:
                query = query.filter(Licitacion.estado == estado)
            
            if fecha_desde:
                query = query.filter(Licitacion.fecha_publicacion >= fecha_desde)
            
            if fecha_hasta:
                query = query.filter(Licitacion.fecha_publicacion <= fecha_hasta)
            
            # Execute query and convert to dict
            licitaciones = query.all()
            return [
                {
                    'id': l.id,
                    'codigo': l.codigo,
                    'titulo': l.titulo,
                    'organismo': l.organismo,
                    'url_fuente': l.url_fuente,
                    'fecha_publicacion': l.fecha_publicacion,
                    'estado': l.estado,
                    'monto': l.monto,
                    'fecha_registro': l.fecha_registro,
                    'datos_extra': json.loads(l.datos_extra) if l.datos_extra else {}
                } for l in licitaciones
            ]
        
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching licitaciones: {e}")
            return []
        finally:
            session.close()

def obtener_persistencia() -> LicitacionesPersistencia:
    """
    Get a LicitacionesPersistencia instance
    
    Returns:
        LicitacionesPersistencia: Persistence instance
    """
    return LicitacionesPersistencia()
