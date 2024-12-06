from typing import List, Dict
import logging
from .comprar_mendoza_template import ComprarMendozaTemplate
from .comprasapps_mendoza_template import ComprasAppsMendozaTemplate
from .comprar_argentina_template import ComprarArgentinaTemplate

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self):
        self.templates = [
            ComprarMendozaTemplate(),
            ComprasAppsMendozaTemplate(),
            ComprarArgentinaTemplate()
        ]

    def extract_all_licitaciones(self) -> List[Dict]:
        """
        Extract licitaciones from all configured templates
        """
        all_licitaciones = []
        
        for template in self.templates:
            try:
                logger.info(f"Extracting licitaciones from {template.url}")
                licitaciones = template.extract_licitaciones()
                logger.info(f"Found {len(licitaciones)} licitaciones from {template.url}")
                all_licitaciones.extend(licitaciones)
            except Exception as e:
                logger.error(f"Error extracting licitaciones from {template.url}: {str(e)}")
                continue

        return all_licitaciones

    def get_template_by_url(self, url: str):
        """
        Get template instance by URL
        """
        for template in self.templates:
            if template.url == url:
                return template
        return None
