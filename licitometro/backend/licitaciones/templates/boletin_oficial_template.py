import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import requests

from .base_template import BaseLicitacionTemplate
from ..logging_config import get_logger

class BoletinOficialTemplate(BaseLicitacionTemplate):
    """
    Template para scraping de licitaciones desde Boletín Oficial
    URL base: https://www.boletinoficial.gob.ar/
    """
    def __init__(self, url: str = 'https://www.boletinoficial.gob.ar/seccion/licitaciones'):
        super().__init__(url)
        self.logger = get_logger(self.__class__.__name__)
        
        # URLs específicas para diferentes tipos de licitaciones
        self.licitacion_urls = [
            'https://www.boletinoficial.gob.ar/seccion/licitaciones-publicas',
            'https://www.boletinoficial.gob.ar/seccion/licitaciones-privadas',
            'https://www.boletinoficial.gob.ar/seccion/concursos-publicos'
        ]

    def extract_licitaciones(self) -> List[Dict]:
        """
        Extraer licitaciones desde múltiples URLs del Boletín Oficial
        """
        licitaciones_totales = []

        for url in self.licitacion_urls:
            try:
                licitaciones_url = self._extract_licitaciones_from_url(url)
                licitaciones_totales.extend(licitaciones_url)
            except Exception as e:
                self.logger.error(f"Error extrayendo licitaciones de {url}: {e}")

        self.logger.info(f"Total licitaciones extraídas: {len(licitaciones_totales)}")
        return licitaciones_totales

    def _extract_licitaciones_from_url(self, url: str) -> List[Dict]:
        """
        Extraer licitaciones de una URL específica
        """
        soup = self.get_page_content(url)
        if not soup:
            return []

        # Selector de lista o tabla de licitaciones (ajustar según estructura real)
        lista_licitaciones = soup.find('div', class_='lista-licitaciones')
        if not lista_licitaciones:
            self.logger.warning(f"No se encontró lista de licitaciones en {url}")
            return []

        licitaciones = []
        elementos_licitacion = lista_licitaciones.find_all('div', class_='licitacion-item')

        for elemento in elementos_licitacion:
            try:
                licitacion = self._parse_elemento_licitacion(elemento, url)
                if licitacion:
                    licitaciones.append(licitacion)
            except Exception as e:
                self.logger.error(f"Error procesando elemento de licitación: {e}")

        return licitaciones

    def _parse_elemento_licitacion(self, elemento, url_fuente: str) -> Optional[Dict]:
        """
        Parsear un elemento individual de licitación
        """
        try:
            # Extraer datos del elemento (ajustar selectores según estructura real)
            titulo_elem = elemento.find('h3', class_='titulo-licitacion')
            organismo_elem = elemento.find('div', class_='organismo')
            fecha_elem = elemento.find('span', class_='fecha')
            monto_elem = elemento.find('div', class_='monto')
            codigo_elem = elemento.find('span', class_='codigo')

            # Extraer texto de los elementos
            titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Sin título"
            organismo = organismo_elem.get_text(strip=True) if organismo_elem else "Sin organismo"
            fecha_str = fecha_elem.get_text(strip=True) if fecha_elem else None
            monto_str = monto_elem.get_text(strip=True) if monto_elem else "0"
            codigo = codigo_elem.get_text(strip=True) if codigo_elem else None

            # Parsear fecha
            fecha_publicacion = self._parse_fecha(fecha_str) if fecha_str else datetime.now()

            # Parsear monto
            monto = self._parse_monto(monto_str)

            # Construir diccionario de licitación
            licitacion = {
                'codigo': codigo,
                'titulo': titulo,
                'organismo': organismo,
                'url_fuente': url_fuente,
                'fecha_publicacion': fecha_publicacion,
                'estado': self._inferir_estado(titulo),
                'monto': monto
            }

            return licitacion

        except Exception as e:
            self.logger.warning(f"Error parseando elemento de licitación: {e}")
            return None

    def _parse_monto(self, monto_str: str) -> float:
        """
        Parsear monto con manejo de diferentes formatos
        """
        try:
            # Remover símbolos de moneda y separadores
            monto_limpio = re.sub(r'[^\d,.]', '', monto_str)
            
            # Reemplazar coma por punto si es separador decimal
            monto_limpio = monto_limpio.replace(',', '.')
            
            return float(monto_limpio)
        except ValueError:
            self.logger.warning(f"No se pudo parsear monto: {monto_str}")
            return 0.0

    def _inferir_estado(self, titulo: str) -> str:
        """
        Inferir estado de la licitación basado en palabras clave
        """
        titulo_lower = titulo.lower()
        
        estados_mapping = {
            'adjudicado': 'Adjudicado',
            'en proceso': 'En Proceso',
            'publicado': 'Publicado',
            'cerrado': 'Cerrado',
            'en curso': 'En Proceso',
            'finalizado': 'Finalizado',
            'abierto': 'Abierto'
        }

        for keyword, estado in estados_mapping.items():
            if keyword in titulo_lower:
                return estado
        
        return 'En Proceso'  # Estado por defecto

    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Obtener contenido de página con manejo de errores
        """
        try:
            response = self.request_manager.get(url, timeout=10)
            if response:
                return BeautifulSoup(response.text, 'html.parser')
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo página {url}: {e}")
            return None
