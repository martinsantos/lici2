from celery import shared_task, states
from sqlalchemy.orm import Session
from core.database import SessionLocal
from . import crud
from .templates import TemplateManager
import logging
import uuid
from datetime import datetime
import traceback
from typing import Dict, Any
from .templates.progress import ScrapingProgress

logger = logging.getLogger(__name__)

class ScrapingProgress:
    def __init__(self):
        self.start_time = datetime.now()
        self.total_found = 0
        self.processed = 0
        self.saved = 0
        self.errors = 0
        self.skipped = 0
        self.current_page = 1
        self.current_status = ""
        self.error_details = []
        self.template_info = {}
        self.last_saved = None
        self.template_name = ""

    def to_dict(self) -> Dict[str, Any]:
        elapsed = datetime.now() - self.start_time
        percent = (self.processed / self.total_found * 100) if self.total_found > 0 else 0
        
        return {
            "total_found": self.total_found,
            "processed": self.processed,
            "saved": self.saved,
            "errors": self.errors,
            "skipped": self.skipped,
            "current_page": self.current_page,
            "current_status": self.current_status,
            "error_details": self.error_details[-10:],  # últimos 10 errores
            "elapsed_time": str(elapsed).split('.')[0],
            "percent_complete": round(percent, 2),
            "template_info": self.template_info,
            "template_name": self.template_name,
            "last_saved": self.last_saved.dict() if self.last_saved else None
        }

    def add_error(self, error_msg):
        self.error_details.append(error_msg)
        self.errors += 1

    def add_success(self, titulo):
        self.saved += 1
        self.last_saved = titulo

def generate_licitacion_id(licitacion_data: dict) -> str:
    """Generate a unique ID for a licitacion based on its data"""
    base = licitacion_data.get('numero_licitacion', '') or \
           f"{licitacion_data.get('titulo', '')}-{licitacion_data.get('organismo', '')}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))

@shared_task(bind=True)
def run_scraping_task(self, template_id: str):
    """Run a scraping task for a specific template with detailed progress updates"""
    progress = ScrapingProgress()
    db = None
    
    def update_state(state: str, meta: dict = None):
        """Update task state with metadata"""
        if meta is None:
            meta = {}
        meta.update(progress.to_dict())
        self.update_state(state=state, meta=meta)
        logger.info(f"Task state: {state} - Progress: {progress.to_dict()}")
    
    try:
        # Initialize database session
        db = SessionLocal()
        
        # Get template
        template = crud.get_template(db, template_id)
        if not template:
            raise ValueError(f"Template {template_id} no encontrado")
        
        if not template.is_active:
            raise ValueError(f"Template {template_id} está inactivo")
        
        # Update template info
        progress.template_name = template.name
        progress.current_status = f'Inicializando scraper para {template.name}'
        update_state('PROGRESS')
        
        # Get scraper for template
        template_manager = TemplateManager()
        scraper = template_manager.get_scraper(template.url)
        scraper.progress = progress  # Asignar el objeto progress al scraper
        
        # Extract licitaciones
        try:
            progress.current_status = f"Extrayendo licitaciones de {template.name}..."
            update_state('PROGRESS')
            
            licitaciones = scraper.extract_licitaciones()
            progress.total_found = len(licitaciones)
            logger.info(f"Found {progress.total_found} licitaciones from {template.name}")
            
            # Save licitaciones
            for idx, licitacion_data in enumerate(licitaciones, 1):
                try:
                    progress.current_status = f'Procesando licitación {idx}/{len(licitaciones)} de {template.name}'
                    progress.processed += 1
                    
                    # Add template info
                    licitacion_data['id'] = generate_licitacion_id(licitacion_data)
                    licitacion_data['template_id'] = template_id
                    licitacion_data['fuente'] = template.name
                    licitacion_data['url_fuente'] = template.url
                    
                    # Validate licitacion
                    if not scraper.validate_licitacion(licitacion_data):
                        error_msg = f"Licitación inválida: {licitacion_data.get('titulo', 'Sin título')}"
                        logger.warning(error_msg)
                        progress.add_error(error_msg)
                        continue
                    
                    # Check if licitacion already exists
                    existing = crud.get_licitacion(db, licitacion_data['id'])
                    if existing:
                        progress.skipped += 1
                        continue
                    
                    # Create licitacion
                    new_licitacion = crud.create_licitacion(db, licitacion_data)
                    progress.add_success(new_licitacion.titulo)
                    logger.info(f"Saved licitacion: {new_licitacion.titulo}")
                    
                except Exception as e:
                    error_msg = f"Error guardando licitación: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    progress.add_error(error_msg)
                    continue
                
                # Update progress every 5 licitaciones
                if idx % 5 == 0:
                    update_state('PROGRESS')
            
            # Final update
            progress.current_status = (
                f"Completado {template.name}: "
                f"{progress.saved} guardadas, "
                f"{progress.errors} errores, "
                f"{progress.skipped} omitidas"
            )
            update_state('SUCCESS')
            
            return progress.to_dict()
            
        except Exception as e:
            error_msg = f"Error en extracción de {template.name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            progress.add_error(error_msg)
            update_state('FAILURE')
            return progress.to_dict()
            
    except Exception as e:
        error_msg = f"Error general en tarea: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        progress.add_error(error_msg)
        update_state('FAILURE')
        return progress.to_dict()
        
    finally:
        if db:
            db.close()
