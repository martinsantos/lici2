import logging
from typing import Dict, List, Any, Optional
from .scraper import ScraperManager
from .database import DatabaseManager
from .models import ScrapingTemplate, ScrapingJob
from .services import ScrapingTemplateService
import json
import os
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataExtractionService:
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializa el servicio de extracción de datos
        
        :param database_url: URL de conexión a la base de datos
        """
        load_dotenv()
        self.database_url = database_url or os.getenv('RECON_DATABASE_URL')
        self.db_manager = DatabaseManager(self.database_url)
        self.template_service = ScrapingTemplateService(self.database_url)

    def extract_data_from_template(self, template_id: int) -> List[Dict[str, Any]]:
        """
        Extrae datos usando una plantilla específica
        
        :param template_id: ID de la plantilla de scraping
        :return: Lista de elementos extraídos
        """
        try:
            # Recuperar plantilla
            template = self.template_service.get_template(template_id)
            
            if not template:
                logger.error(f"Plantilla con ID {template_id} no encontrada")
                return []

            # Convertir modelo SQLAlchemy a diccionario
            template_dict = {
                'source_url': template.source_url,
                'field_mapping': template.field_mapping,
                'transformation_rules': template.transformation_rules,
                'item_selector': template.get('item_selector', 'div.item'),
                'pagination': {
                    'enabled': True,
                    'selector': template.get('next_page_selector')
                },
                'max_pages': template.get('max_pages', 3)
            }

            # Crear trabajo de scraping
            job = self._create_scraping_job(template_id)

            # Ejecutar scraping
            results = ScraperManager.run_scraper(template_dict)

            # Actualizar estado del trabajo
            self._update_job_status(job.id, results)

            return results

        except Exception as e:
            logger.error(f"Error en extracción de datos: {e}")
            return []

    def _create_scraping_job(self, template_id: int) -> ScrapingJob:
        """
        Crea un nuevo trabajo de scraping
        
        :param template_id: ID de la plantilla
        :return: Objeto de trabajo de scraping
        """
        with self.db_manager.get_session() as session:
            job = ScrapingJob(template_id=template_id)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job

    def _update_job_status(self, job_id: int, results: List[Dict[str, Any]]):
        """
        Actualiza el estado de un trabajo de scraping
        
        :param job_id: ID del trabajo
        :param results: Resultados extraídos
        """
        with self.db_manager.get_session() as session:
            job = session.query(ScrapingJob).filter_by(id=job_id).first()
            if job:
                job.status = 'completed'
                job.items_scraped = len(results)
                session.commit()

    def extract_data_from_all_templates(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Extrae datos de todas las plantillas activas
        
        :return: Diccionario con resultados por plantilla
        """
        active_templates = self.template_service.list_templates(is_active=True)
        
        results = {}
        for template in active_templates:
            template_results = self.extract_data_from_template(template.id)
            results[template.id] = template_results

        return results

    def save_extracted_data(self, template_id: int, data: List[Dict[str, Any]]):
        """
        Guarda los datos extraídos en la base de datos
        
        :param template_id: ID de la plantilla
        :param data: Datos extraídos
        """
        # Implementación pendiente: guardar en Elasticsearch o base de datos
        logger.info(f"Guardando {len(data)} elementos de la plantilla {template_id}")

# Ejemplo de uso
if __name__ == '__main__':
    extraction_service = DataExtractionService()
    
    # Extraer datos de una plantilla específica
    results = extraction_service.extract_data_from_template(1)
    
    # Guardar resultados en un archivo JSON (opcional)
    with open('extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Extraer datos de todas las plantillas activas
    all_results = extraction_service.extract_data_from_all_templates()
    print(json.dumps(all_results, indent=2, ensure_ascii=False))
