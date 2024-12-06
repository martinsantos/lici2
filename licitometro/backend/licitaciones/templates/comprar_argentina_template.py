from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base_template import BaseLicitacionTemplate, logger

class ComprarArgentinaTemplate(BaseLicitacionTemplate):
    def __init__(self):
        super().__init__("https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10=")

    def _find_main_container(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Find the main container for licitaciones in the parsed HTML.
        """
        try:
            # Try different possible table selectors
            possible_selectors = [
                {'id': 'dgLicitaciones'},  # Old structure
                {'id': 'CPH1_GridListaPliegosAperturaProxima'},  # New structure
                {'class': 'table'},  # Generic table
            ]
            
            for selector in possible_selectors:
                table = soup.find('table', selector)
                if table:
                    return table

            # Try finding any table that looks like it contains licitaciones
            all_tables = soup.find_all('table')
            for t in all_tables:
                # Check if table has enough columns and looks like a licitaciones table
                header_row = t.find('tr')
                if header_row and len(header_row.find_all(['th', 'td'])) >= 6:
                    return t

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
            
            # Get all rows, skipping the header row
            rows = main_container.find_all('tr')[1:]
            return rows

        except Exception as e:
            logger.warning(f"Error finding licitacion elements: {str(e)}")
            return []

    def _extract_licitacion_details(self, element: Any) -> Optional[Dict]:
        """
        Extract details for a single licitacion from an element.
        """
        try:
            # Find all cells in the row
            cells = element.find_all('td')
            
            # Check if we have enough cells
            if len(cells) < 6:
                return None

            # Extract text from cells
            titulo = self.clean_text(cells[1].get_text())
            organismo = self.clean_text(cells[2].get_text())
            estado = self.clean_text(cells[3].get_text())
            fecha_pub_text = self.clean_text(cells[4].get_text())
            fecha_ap_text = self.clean_text(cells[5].get_text())

            # Process dates
            fecha_publicacion = None
            fecha_apertura = None

            # Try to extract publication date
            if fecha_pub_text:
                fecha_publicacion = self.extract_date_from_text(fecha_pub_text)
                if fecha_publicacion:
                    fecha_publicacion = self.parse_date(fecha_publicacion)

            # Try to extract opening date
            if fecha_ap_text:
                fecha_apertura = self.extract_date_from_text(fecha_ap_text)
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

            # Optional: Extract monto if available (assuming it's in the 6th cell)
            if len(cells) > 6:
                monto_text = self.clean_text(cells[6].get_text())
                if monto_text:
                    try:
                        # Remove currency symbols and separators
                        monto_text = re.sub(r'[^\d,.]', '', monto_text)
                        monto = float(monto_text.replace('.', '').replace(',', '.'))
                        licitacion['monto'] = monto
                        licitacion['moneda'] = 'ARS'  # Assuming Argentine Pesos
                    except ValueError:
                        logger.warning(f"Could not parse monto: {monto_text}")

            return licitacion

        except Exception as e:
            logger.warning(f"Error extracting licitacion details: {str(e)}")
            return None

    def extract_licitaciones(self) -> List[Dict]:
        """
        Extract licitaciones from Comprar Argentina
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
