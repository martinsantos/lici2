import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ComprarClient:
    """Cliente para el sistema COMPR.AR de Argentina"""
    
    BASE_URL = "https://comprar.gob.ar"
    SEARCH_URL = f"{BASE_URL}/buscar"
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def buscar_licitaciones(
        self,
        query: str,
        max_results: int = 100,
        filtros: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca licitaciones en COMPR.AR
        
        Args:
            query: Términos de búsqueda
            max_results: Número máximo de resultados
            filtros: Filtros adicionales (opcional)
                - fecha_desde: Fecha inicio (YYYY-MM-DD)
                - fecha_hasta: Fecha fin (YYYY-MM-DD)
                - estado: Estado de la licitación
                - organismo: Organismo comprador
        
        Returns:
            Lista de licitaciones encontradas
        """
        try:
            params = {
                'searchQuery': query,
                'pageSize': min(max_results, 100),
                'page': 1
            }
            
            # Agregar filtros si existen
            if filtros:
                if 'fecha_desde' in filtros:
                    params['fromDate'] = filtros['fecha_desde']
                if 'fecha_hasta' in filtros:
                    params['toDate'] = filtros['fecha_hasta']
                if 'estado' in filtros:
                    params['status'] = filtros['estado']
                if 'organismo' in filtros:
                    params['agency'] = filtros['organismo']
            
            async with self.session.get(
                self.SEARCH_URL,
                params=params
            ) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_resultados(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error en la búsqueda COMPR.AR: {str(e)}")
            raise
    
    def _parsear_resultados(self, html: str) -> List[Dict]:
        """Parsea los resultados de la búsqueda"""
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []
        
        for item in soup.select('.tender-item'):
            try:
                resultado = {
                    'id': item.get('data-tender-id'),
                    'titulo': item.select_one('.tender-title').text.strip(),
                    'organismo': item.select_one('.agency-name').text.strip(),
                    'tipo': item.select_one('.tender-type').text.strip(),
                    'estado': item.select_one('.tender-status').text.strip(),
                    'fecha_publicacion': item.select_one('.publish-date').text.strip(),
                    'fecha_apertura': item.select_one('.opening-date').text.strip(),
                    'monto_estimado': item.select_one('.estimated-amount').text.strip(),
                    'url': f"{self.BASE_URL}{item.select_one('a')['href']}"
                }
                
                resultados.append(resultado)
                
            except (AttributeError, KeyError) as e:
                logger.warning(f"Error parseando resultado: {str(e)}")
                continue
        
        return resultados
    
    async def obtener_detalle(self, licitacion_id: str) -> Dict:
        """
        Obtiene el detalle de una licitación específica
        
        Args:
            licitacion_id: ID de la licitación
            
        Returns:
            Detalles de la licitación
        """
        try:
            url = f"{self.BASE_URL}/tender/{licitacion_id}"
            
            async with self.session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_detalle(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error obteniendo detalle: {str(e)}")
            raise
    
    def _parsear_detalle(self, html: str) -> Dict:
        """Parsea los detalles de una licitación"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            detalle = {
                'numero_proceso': soup.select_one('.process-number').text.strip(),
                'objeto': soup.select_one('.tender-object').text.strip(),
                'descripcion': soup.select_one('.description').text.strip(),
                'organismo': soup.select_one('.agency-details').text.strip(),
                'tipo_contratacion': soup.select_one('.contract-type').text.strip(),
                'estado': soup.select_one('.status').text.strip(),
                'moneda': soup.select_one('.currency').text.strip(),
                'monto_estimado': soup.select_one('.amount').text.strip(),
                'fecha_publicacion': soup.select_one('.publish-date').text.strip(),
                'fecha_apertura': soup.select_one('.opening-date').text.strip(),
                'pliego': {
                    'url': soup.select_one('.download-specs a')['href'],
                    'fecha': soup.select_one('.specs-date').text.strip()
                },
                'items': self._parsear_items(soup),
                'documentos': self._parsear_documentos(soup)
            }
            
            return detalle
            
        except (AttributeError, KeyError) as e:
            logger.error(f"Error parseando detalle: {str(e)}")
            raise
    
    def _parsear_items(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los items de la licitación"""
        items = []
        
        for item in soup.select('.tender-item'):
            try:
                items.append({
                    'codigo': item.select_one('.item-code').text.strip(),
                    'descripcion': item.select_one('.item-description').text.strip(),
                    'cantidad': item.select_one('.quantity').text.strip(),
                    'unidad': item.select_one('.unit').text.strip()
                })
            except (AttributeError, KeyError):
                continue
                
        return items
    
    def _parsear_documentos(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los documentos adjuntos"""
        documentos = []
        
        for doc in soup.select('.document-item'):
            try:
                documentos.append({
                    'nombre': doc.select_one('.doc-name').text.strip(),
                    'tipo': doc.select_one('.doc-type').text.strip(),
                    'fecha': doc.select_one('.doc-date').text.strip(),
                    'url': doc.select_one('a')['href']
                })
            except (AttributeError, KeyError):
                continue
                
        return documentos
