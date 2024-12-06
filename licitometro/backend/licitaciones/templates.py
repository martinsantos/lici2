from typing import Optional
from .scraper import BaseScraper, ComprarMendozaScraper, ComprasAppsMendozaScraper, ComprarArgentinaScraper
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self):
        self.templates = {
            "https://comprar.mendoza.gov.ar/Compras.aspx?qs=W1HXHGHtH10=": ComprarMendozaScraper,
            "https://comprasapps.mendoza.gov.ar/Compras/servlet/hli00049": ComprasAppsMendozaScraper,
            "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10=": ComprarArgentinaScraper
        }

    def get_template_by_url(self, url: str) -> Optional[BaseScraper]:
        """Get a scraper instance for the given URL"""
        try:
            scraper_class = self.templates.get(url)
            if scraper_class:
                return scraper_class(url)
            logger.warning(f"No scraper found for URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Error creating scraper for URL {url}: {str(e)}")
            return None
