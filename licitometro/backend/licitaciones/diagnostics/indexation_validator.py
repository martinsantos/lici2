import logging
from typing import Dict, List, Any
from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import re
import uuid
from typing import Optional

# Import core database configuration
from ....core.database import engine, Base, get_db

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LicitacionModel(Base):
    """
    Modelo de base de datos para diagnóstico de indexación con mayor tolerancia
    """
    __tablename__ = 'licitaciones_diagnostico'

    id = Column(String, primary_key=True)
    titulo = Column(String, nullable=False)
    organismo = Column(String, nullable=False)
    estado = Column(String, nullable=True, server_default='En Proceso')
    fecha_publicacion = Column(DateTime(timezone=True), nullable=True)
    fecha_apertura = Column(DateTime(timezone=True), nullable=True)
    monto = Column(Float, nullable=True, server_default='0.0')
    url_fuente = Column(String, nullable=True)
    url = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)

    def __init__(self, **kwargs):
        # Convertir datetime a ISO para serialización
        if 'raw_data' in kwargs:
            raw_data = kwargs['raw_data']
            for k, v in raw_data.items():
                if isinstance(v, datetime):
                    raw_data[k] = v.isoformat()
        
        # Valores por defecto
        kwargs.setdefault('estado', 'En Proceso')
        kwargs.setdefault('monto', 0.0)
        
        # Usar fecha de apertura si no hay fecha de publicación
        if not kwargs.get('fecha_publicacion') and kwargs.get('fecha_apertura'):
            kwargs['fecha_publicacion'] = kwargs['fecha_apertura']
        
        super().__init__(**kwargs)

class IndexationDiagnostics:
    def __init__(self):
        """
        Inicializar diagnóstico de indexación con estrategias de recuperación
        """
        self.Session = sessionmaker(bind=engine)
        self.logger = logger

    def generate_unique_id(self, licitacion: Dict) -> str:
        """
        Estrategia robusta de generación de ID único con múltiples fallbacks
        """
        # Prioridad en la generación de ID
        id_strategies = [
            licitacion.get('id'),  # ID existente
            licitacion.get('numero_licitacion'),  # Número de licitación
            licitacion.get('numero_expediente'),  # Número de expediente
            f"{licitacion.get('organismo', 'SIN_ORG')}-{licitacion.get('titulo', 'SIN_TITULO')[:50]}",  # Combinación de organismo y título
            str(uuid.uuid4())  # UUID completamente aleatorio como último recurso
        ]

        # Tomar el primer ID no vacío
        for strategy in id_strategies:
            if strategy:
                # Truncar a 100 caracteres y limpiar
                clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', str(strategy)[:100])
                return clean_id

    def _parse_date_flexibly(self, date_str: str) -> Optional[datetime]:
        """
        Parseo flexible de fechas con múltiples estrategias
        """
        # Formatos de fecha a intentar
        date_formats = [
            "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", 
            "%m/%d/%Y", "%Y/%m/%d", "%d/%m/%y",
            "%y/%m/%d", "%m/%d/%y", "%d-%m-%y"
        ]

        # Limpiar cadena de fecha
        date_str = re.sub(r'\s+', ' ', str(date_str).strip())

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def validate_licitacion_for_db(self, licitacion: Dict) -> Dict[str, Any]:
        """
        Validación y recuperación de campos con estrategias de completado
        """
        diagnostics = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'processed_licitacion': {}
        }

        # Campos con valores por defecto y estrategias de recuperación
        field_recovery_strategies = {
            'titulo': [
                licitacion.get('titulo'),
                'Licitación Sin Título'
            ],
            'organismo': [
                licitacion.get('organismo'),
                'Organismo No Especificado'
            ],
            'estado': [
                licitacion.get('estado', 'En Proceso')  # Valor por defecto
            ],
            'fecha_publicacion': [
                licitacion.get('fecha_publicacion'),
                licitacion.get('fecha_apertura'),  # Fallback a fecha de apertura
                datetime.now().strftime("%Y-%m-%d")  # Fecha actual como último recurso
            ],
            'url_fuente': [
                licitacion.get('url_fuente'),
                licitacion.get('url'),
                'URL No Disponible'
            ]
        }

        # Recuperación de campos con estrategias de fallback
        for field, strategies in field_recovery_strategies.items():
            value = next((v for v in strategies if v), None)
            licitacion[field] = value
            if not value:
                diagnostics['warnings'].append(f"No se pudo recuperar el campo: {field}")

        # Generación de ID único con estrategias de recuperación
        licitacion['id'] = self.generate_unique_id(licitacion)

        # Estrategia robusta de conversión de fechas
        date_fields = ['fecha_publicacion', 'fecha_apertura']
        for field in date_fields:
            if licitacion.get(field):
                try:
                    # Intentar parsear la fecha
                    parsed_date = self._parse_date_flexibly(licitacion[field])
                    licitacion[field] = parsed_date
                except Exception as e:
                    diagnostics['warnings'].append(f"Error parseando fecha {field}: {str(e)}")
                    licitacion[field] = None

        return diagnostics

    def save_licitacion(self, licitacion: Dict) -> Dict[str, Any]:
        """
        Guardar licitación con validación y diagnóstico
        """
        try:
            # Validar licitación
            diagnostics = self.validate_licitacion_for_db(licitacion)

            # Crear sesión
            session = next(get_db())

            # Crear modelo de licitación
            db_licitacion = LicitacionModel(
                id=licitacion['id'],
                titulo=licitacion['titulo'],
                organismo=licitacion['organismo'],
                estado=licitacion.get('estado', 'En Proceso'),
                fecha_publicacion=licitacion.get('fecha_publicacion'),
                fecha_apertura=licitacion.get('fecha_apertura'),
                monto=licitacion.get('monto', 0.0),
                url_fuente=licitacion.get('url_fuente'),
                url=licitacion.get('url'),
                raw_data=licitacion
            )

            # Agregar y confirmar
            session.merge(db_licitacion)
            session.commit()

            diagnostics['processed_licitacion'] = licitacion
            return diagnostics

        except SQLAlchemyError as e:
            self.logger.error(f"Error guardando licitación: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
        finally:
            session.close()

def diagnose_indexation(licitaciones: List[Dict]) -> List[Dict]:
    """
    Función principal de diagnóstico de indexación
    """
    diagnostics = IndexationDiagnostics()
    results = []

    for licitacion in licitaciones:
        result = diagnostics.save_licitacion(licitacion)
        results.append(result)

    return results

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de licitaciones para prueba
    licitaciones_ejemplo = [
        {
            'titulo': 'Licitación de Prueba',
            'organismo': 'Organismo de Prueba',
            'fecha_publicacion': '2023-01-15',
            'monto': 1000000.0
        }
    ]

    resultados = diagnose_indexation(licitaciones_ejemplo)
    print(resultados)
