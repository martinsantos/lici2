import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re

from .base_template import BaseLicitacionTemplate
from ..logging_config import get_logger

class ComprarTemplate(BaseLicitacionTemplate):
    """
    Template para scraping de licitaciones desde comprar.gob.ar
    """
    def __init__(self, url: str = 'https://comprar.gob.ar/Compras.aspx'):
        super().__init__(url)
        self.logger = get_logger(self.__class__.__name__)

    def extract_licitaciones(self) -> List[Dict]:
        """
        Extraer licitaciones desde comprar.gob.ar
        """
        try:
            # Obtener contenido de la página
            soup = self.get_page_content(self.url)
            if not soup:
                self.logger.warning(f"No se pudo obtener contenido de {self.url}")
                return []

            # Buscar tabla de licitaciones (ajustar selectores según estructura real)
            tabla_licitaciones = soup.find('table', class_='tabla-licitaciones')
            if not tabla_licitaciones:
                self.logger.warning("No se encontró tabla de licitaciones")
                return []

            licitaciones = []
            filas = tabla_licitaciones.find_all('tr')[1:]  # Saltar encabezado

            for fila in filas:
                try:
                    licitacion = self._parse_fila_licitacion(fila)
                    if licitacion:
                        licitaciones.append(licitacion)
                except Exception as e:
                    self.logger.error(f"Error procesando fila: {e}")

            self.logger.info(f"Extraídas {len(licitaciones)} licitaciones")
            return licitaciones

        except Exception as e:
            self.logger.error(f"Error en extracción de licitaciones: {e}")
            return []

    def _parse_fila_licitacion(self, fila) -> Optional[Dict]:
        """
        Parsear una fila individual de licitación
        """
        celdas = fila.find_all('td')
        if len(celdas) < 4:
            return None

        try:
            # Extraer datos de las celdas (ajustar índices según estructura real)
            numero_licitacion = celdas[0].get_text(strip=True)
            titulo = celdas[1].get_text(strip=True)
            organismo = celdas[2].get_text(strip=True)
            fecha_str = celdas[3].get_text(strip=True)

            # Parsear fecha
            fecha_publicacion = self._parse_fecha(fecha_str)

            # Construir diccionario de licitación
            licitacion = {
                'numero_licitacion': numero_licitacion,
                'titulo': titulo,
                'organismo': organismo,
                'url_fuente': self.url,
                'fecha_publicacion': fecha_publicacion,
                'estado': self._inferir_estado(titulo)
            }

            return licitacion

        except Exception as e:
            self.logger.warning(f"Error parseando fila de licitación: {e}")
            return None

    def _parse_fecha(self, fecha_str: str) -> datetime:
        """
        Parsear fecha con formatos flexibles
        """
        for formato in self.DATE_FORMATS:
            try:
                return datetime.strptime(fecha_str, formato)
            except ValueError:
                continue
        
        # Fallback: fecha actual si no se puede parsear
        self.logger.warning(f"Formato de fecha no reconocido: {fecha_str}")
        return datetime.now()

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
            'en curso': 'En Proceso'
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
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Error obteniendo página {url}: {e}")
            return None
