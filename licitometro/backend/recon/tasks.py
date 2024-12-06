from celery import Celery, Task
from celery.schedules import crontab
from .extraction_service import DataExtractionService
from .services import ScrapingTemplateService
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de Celery
app = Celery(
    'recon_tasks', 
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Configuraciones de Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

class ScrapingTask(Task):
    """
    Clase base para tareas de scraping con manejo de reintentos
    """
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutos
    retry_jitter = True

@app.task(base=ScrapingTask, bind=True)
def run_scraping_template(self, template_id: int):
    """
    Tarea para ejecutar scraping de una plantilla específica
    
    :param template_id: ID de la plantilla de scraping
    """
    try:
        logger.info(f"Iniciando scraping para plantilla {template_id}")
        
        # Inicializar servicio de extracción
        extraction_service = DataExtractionService()
        
        # Extraer datos
        results = extraction_service.extract_data_from_template(template_id)
        
        # Guardar datos extraídos
        extraction_service.save_extracted_data(template_id, results)
        
        logger.info(f"Scraping completado para plantilla {template_id}. Elementos extraídos: {len(results)}")
        
        return {
            'template_id': template_id,
            'items_scraped': len(results)
        }
    
    except Exception as exc:
        logger.error(f"Error en scraping de plantilla {template_id}: {exc}")
        raise self.retry(exc=exc)

@app.task
def run_all_scraping_templates():
    """
    Tarea para ejecutar scraping de todas las plantillas activas
    """
    try:
        logger.info("Iniciando scraping para todas las plantillas activas")
        
        # Inicializar servicio de plantillas
        template_service = ScrapingTemplateService()
        
        # Obtener plantillas activas
        active_templates = template_service.list_templates(is_active=True)
        
        # Ejecutar scraping para cada plantilla
        results = {}
        for template in active_templates:
            task = run_scraping_template.delay(template.id)
            results[template.id] = task.id
        
        logger.info(f"Tareas de scraping iniciadas para {len(active_templates)} plantillas")
        
        return results
    
    except Exception as exc:
        logger.error(f"Error en scraping global: {exc}")
        raise

# Configuración de tareas programadas
app.conf.beat_schedule = {
    'run-all-scraping-templates-daily': {
        'task': 'tasks.run_all_scraping_templates',
        'schedule': crontab(hour=2, minute=0),  # Ejecutar diariamente a las 2 AM
    },
}

# Ejemplo de uso directo
if __name__ == '__main__':
    # Ejecutar scraping de una plantilla específica
    result = run_scraping_template(1)
    print(result)
    
    # Ejecutar scraping de todas las plantillas
    all_results = run_all_scraping_templates()
    print(all_results)
