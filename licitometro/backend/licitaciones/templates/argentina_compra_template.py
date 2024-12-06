from .base_template import BaseLicitacionTemplate
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re

from ..logging_config import get_logger

class ArgentinaCompraTemplate(BaseLicitacionTemplate):
    """
    Template para scraping de licitaciones desde argentina.gob.ar/compras
    """
    def __init__(self, url: str = 'https://www.argentina.gob.ar/compras'):
        super().__init__(url)
        self.logger = get_logger(self.__class__.__name__)
        
        # URLs específicas para diferentes tipos de licitaciones
        self.licitacion_urls = [
            'https://www.argentina.gob.ar/compras/licitaciones-publicas',
            'https://www.argentina.gob.ar/compras/contrataciones-directas',
            'https://www.argentina.gob.ar/compras/concursos-publicos'
        ]

    def extract_licitaciones(self) -> List[Dict]:
        """
        Extraer licitaciones desde múltiples URLs de Argentina Compra
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

        # Selector de tabla de licitaciones (ajustar según estructura real)
        tabla_licitaciones = soup.find('table', class_='tabla-licitaciones')
        if not tabla_licitaciones:
            self.logger.warning(f"No se encontró tabla de licitaciones en {url}")
            return []

        licitaciones = []
        filas = tabla_licitaciones.find_all('tr')[1:]  # Saltar encabezado

        for fila in filas:
            try:
                licitacion = self._parse_fila_licitacion(fila, url)
                if licitacion:
                    licitaciones.append(licitacion)
            except Exception as e:
                self.logger.error(f"Error procesando fila: {e}")

        return licitaciones

    def _parse_fila_licitacion(self, fila, url_fuente: str) -> Optional[Dict]:
        """
        Parsear una fila individual de licitación
        """
        celdas = fila.find_all('td')
        if len(celdas) < 5:  # Ajustar según estructura real
            return None

        try:
            # Extraer datos de las celdas (ajustar índices según estructura real)
            codigo = celdas[0].get_text(strip=True)
            titulo = celdas[1].get_text(strip=True)
            organismo = celdas[2].get_text(strip=True)
            monto_str = celdas[3].get_text(strip=True)
            fecha_str = celdas[4].get_text(strip=True)

            # Parsear monto
            monto = self._parse_monto(monto_str)

            # Parsear fecha
            fecha_publicacion = self._parse_fecha(fecha_str)

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
            'finalizado': 'Finalizado'
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
