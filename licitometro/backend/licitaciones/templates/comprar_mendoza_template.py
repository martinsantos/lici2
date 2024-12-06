from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base_template import BaseLicitacionTemplate, logger

class ComprarMendozaTemplate(BaseLicitacionTemplate):
    def __init__(self):
        super().__init__("https://comprar.mendoza.gov.ar/Compras.aspx?qs=W1HXHGHtH10=")

    def _find_main_container(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Find the main container for licitaciones in the parsed HTML.
        """
        try:
            table = soup.find('table', {'class': 'table'})
            if not table:
                logger.warning("No table found with class 'table'")
            return table
        except Exception as e:
            logger.warning(f"Error finding main container: {str(e)}")
            return None

    def _find_licitacion_elements(self, main_container: Any) -> List[Any]:
        """
        Find individual licitacion elements within the main container.
        """
        try:
            if not main_container:
                return []
            
            rows = main_container.find_all('tr')[1:]  # Skip header row
            return rows
        except Exception as e:
            logger.warning(f"Error finding licitacion elements: {str(e)}")
            return []

    def _extract_licitacion_details(self, element: Any) -> Optional[Dict]:
        """
        Extract details for a single licitacion from an element.
        """
        try:
            cells = element.find_all('td')
            if len(cells) < 6:
                return None

            # Extract and clean text from cells
            titulo = self.clean_text(cells[1].get_text())
            organismo = self.clean_text(cells[2].get_text())
            estado = self.clean_text(cells[3].get_text())
            fecha_pub = self.clean_text(cells[4].get_text())
            fecha_ap = self.clean_text(cells[5].get_text())

            # Process dates
            fecha_publicacion = None
            fecha_apertura = None
            
            # Try to extract publication date
            if fecha_pub:
                fecha_publicacion = self.extract_date_from_text(fecha_pub)
                if fecha_publicacion:
                    fecha_publicacion = self.parse_date(fecha_publicacion)

            # Try to extract opening date
            if fecha_ap:
                fecha_apertura = self.extract_date_from_text(fecha_ap)
                if fecha_apertura:
                    fecha_apertura = self.parse_date(fecha_apertura)

            # Create licitacion dictionary
            licitacion = {
                'titulo': titulo,
                'organismo': organismo,
                'estado': estado or 'Pendiente',
                'fecha_publicacion': fecha_publicacion,
                'fecha_apertura': fecha_apertura,
                'url_licitacion': self.url
            }

            return licitacion

        except Exception as e:
            logger.warning(f"Error extracting licitacion details: {str(e)}")
            return None

    def extract_licitaciones(self) -> List[Dict]:
        """
        Extract licitaciones from Comprar Mendoza
        """
        licitaciones = []
        soup = self.get_page_content(self.url)
        
        if not soup:
            return licitaciones

        # Use the new methods to extract licitaciones
        main_container = self._find_main_container(soup)
        if not main_container:
            return licitaciones

        licitacion_elements = self._find_licitacion_elements(main_container)
        
        for element in licitacion_elements:
            licitacion = self._extract_licitacion_details(element)
            if licitacion:
                licitaciones.append(licitacion)

        return licitaciones
