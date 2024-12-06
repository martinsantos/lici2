from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base_template import BaseLicitacionTemplate, logger

class ComprasAppsMendozaTemplate(BaseLicitacionTemplate):
    def __init__(self):
        super().__init__("https://comprasapps.mendoza.gov.ar/Compras/servlet/hli00049")

    def _find_main_container(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Find the main container for licitaciones in the parsed HTML.
        """
        try:
            # Try different possible container structures
            possible_containers = [
                soup.find('div', {'class': 'container-fluid'}),
                soup.find('div', {'class': 'container'}),
                soup.find('div', {'role': 'main'}),
                soup.find('main'),
                soup.find('div', {'id': 'main-content'}),
            ]
            
            for container in possible_containers:
                if container:
                    return container
                    
            # Try to find any div that might contain licitaciones
            content_divs = soup.find_all('div', class_=True)
            for div in content_divs:
                # Look for divs that have multiple child rows or items
                if len(div.find_all('div', recursive=False)) > 2:
                    return div

            logger.warning("No main container found for licitaciones")
            return None

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
            
            # Try different strategies to find licitacion elements
            licitacion_strategies = [
                lambda: main_container.find_all('div', {'class': 'licitacion'}),
                lambda: main_container.find_all('tr', {'class': 'licitacion-row'}),
                lambda: main_container.find_all('div', class_=re.compile(r'licitacion|item')),
                lambda: main_container.find_all(['tr', 'div'], recursive=True)
            ]

            for strategy in licitacion_strategies:
                elements = strategy()
                if elements and len(elements) > 0:
                    return elements

            logger.warning("No licitacion elements found")
            return []

        except Exception as e:
            logger.warning(f"Error finding licitacion elements: {str(e)}")
            return []

    def _extract_licitacion_details(self, element: Any) -> Optional[Dict]:
        """
        Extract details for a single licitacion from an element.
        """
        try:
            # Try to extract text from various possible child elements
            text_strategies = [
                lambda: element.get_text(separator=' ', strip=True),
                lambda: ' '.join([cell.get_text(strip=True) for cell in element.find_all(['td', 'div'])]),
            ]

            full_text = None
            for strategy in text_strategies:
                try:
                    full_text = strategy()
                    if full_text:
                        break
                except Exception:
                    continue

            if not full_text:
                return None

            # Extract key details using regex and text parsing
            titulo_match = re.search(r'Licitación\s*[Nº]?\s*(\d+)?\s*(.+?)(?=Organismo|Fecha|$)', full_text, re.IGNORECASE)
            titulo = titulo_match.group(2).strip() if titulo_match else 'Sin título'

            organismo_match = re.search(r'Organismo\s*:?\s*(.+?)(?=Fecha|$)', full_text, re.IGNORECASE)
            organismo = organismo_match.group(1).strip() if organismo_match else 'Sin organismo'

            # Try to extract dates
            fecha_pub_match = re.search(r'Fecha\s*Publicación\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text, re.IGNORECASE)
            fecha_ap_match = re.search(r'Fecha\s*Apertura\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text, re.IGNORECASE)

            # Parse dates
            fecha_publicacion = None
            fecha_apertura = None

            if fecha_pub_match:
                fecha_publicacion = self.extract_date_from_text(fecha_pub_match.group(1))
                if fecha_publicacion:
                    fecha_publicacion = self.parse_date(fecha_publicacion)

            if fecha_ap_match:
                fecha_apertura = self.extract_date_from_text(fecha_ap_match.group(1))
                if fecha_apertura:
                    fecha_apertura = self.parse_date(fecha_apertura)

            # Create licitacion dictionary
            licitacion = {
                'titulo': titulo,
                'organismo': organismo,
                'estado': 'Pendiente',
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
        Extract licitaciones from Compras Apps Mendoza
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
