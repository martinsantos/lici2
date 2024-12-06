import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BACClient:
    """Cliente para el sistema Buenos Aires Compras (BAC)"""
    
    BASE_URL = "https://buenosairescompras.gob.ar"
    SEARCH_URL = f"{BASE_URL}/procesos-de-compra"
    
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
        Busca licitaciones en Buenos Aires Compras
        
        Args:
            query: Términos de búsqueda
            max_results: Número máximo de resultados
            filtros: Filtros adicionales (opcional)
                - fecha_desde: Fecha inicio (YYYY-MM-DD)
                - fecha_hasta: Fecha fin (YYYY-MM-DD)
                - estado: Estado del proceso
                - tipo: Tipo de proceso
                - reparticion: Repartición compradora
        
        Returns:
            Lista de licitaciones encontradas
        """
        try:
            params = {
                'texto': query,
                'cantidadRegistros': min(max_results, 100),
                'pagina': 1
            }
            
            # Agregar filtros si existen
            if filtros:
                if 'fecha_desde' in filtros:
                    params['fechaDesde'] = filtros['fecha_desde']
                if 'fecha_hasta' in filtros:
                    params['fechaHasta'] = filtros['fecha_hasta']
                if 'estado' in filtros:
                    params['estado'] = filtros['estado']
                if 'tipo' in filtros:
                    params['tipo'] = filtros['tipo']
                if 'reparticion' in filtros:
                    params['reparticion'] = filtros['reparticion']
            
            async with self.session.get(
                self.SEARCH_URL,
                params=params
            ) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_resultados(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error en la búsqueda BAC: {str(e)}")
            raise
    
    def _parsear_resultados(self, html: str) -> List[Dict]:
        """Parsea los resultados de la búsqueda"""
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []
        
        for item in soup.select('.proceso-compra'):
            try:
                resultado = {
                    'numero': item.select_one('.numero-proceso').text.strip(),
                    'nombre': item.select_one('.nombre-proceso').text.strip(),
                    'reparticion': item.select_one('.reparticion').text.strip(),
                    'tipo': item.select_one('.tipo-proceso').text.strip(),
                    'estado': item.select_one('.estado').text.strip(),
                    'fecha_publicacion': item.select_one('.fecha-publicacion').text.strip(),
                    'fecha_apertura': item.select_one('.fecha-apertura').text.strip(),
                    'monto_estimado': item.select_one('.monto').text.strip(),
                    'url': f"{self.BASE_URL}{item.select_one('a')['href']}"
                }
                
                resultados.append(resultado)
                
            except (AttributeError, KeyError) as e:
                logger.warning(f"Error parseando resultado: {str(e)}")
                continue
        
        return resultados
    
    async def obtener_detalle(self, proceso_id: str) -> Dict:
        """
        Obtiene el detalle de un proceso de compra específico
        
        Args:
            proceso_id: ID del proceso
            
        Returns:
            Detalles del proceso
        """
        try:
            url = f"{self.BASE_URL}/proceso/{proceso_id}"
            
            async with self.session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_detalle(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error obteniendo detalle: {str(e)}")
            raise
    
    def _parsear_detalle(self, html: str) -> Dict:
        """Parsea los detalles de un proceso"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            detalle = {
                'numero_proceso': soup.select_one('.numero-proceso').text.strip(),
                'nombre': soup.select_one('.nombre-proceso').text.strip(),
                'descripcion': soup.select_one('.descripcion').text.strip(),
                'reparticion': {
                    'nombre': soup.select_one('.reparticion-nombre').text.strip(),
                    'direccion': soup.select_one('.reparticion-direccion').text.strip(),
                    'contacto': soup.select_one('.reparticion-contacto').text.strip()
                },
                'tipo_proceso': soup.select_one('.tipo-proceso').text.strip(),
                'estado': soup.select_one('.estado').text.strip(),
                'moneda': soup.select_one('.moneda').text.strip(),
                'monto_estimado': soup.select_one('.monto').text.strip(),
                'fechas': {
                    'publicacion': soup.select_one('.fecha-publicacion').text.strip(),
                    'apertura_ofertas': soup.select_one('.fecha-apertura').text.strip(),
                    'visita': soup.select_one('.fecha-visita').text.strip(),
                    'consultas_hasta': soup.select_one('.fecha-consultas').text.strip()
                },
                'etapas': self._parsear_etapas(soup),
                'items': self._parsear_items(soup),
                'documentos': self._parsear_documentos(soup)
            }
            
            return detalle
            
        except (AttributeError, KeyError) as e:
            logger.error(f"Error parseando detalle: {str(e)}")
            raise
    
    def _parsear_etapas(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea las etapas del proceso"""
        etapas = []
        
        for etapa in soup.select('.etapa'):
            try:
                etapas.append({
                    'nombre': etapa.select_one('.etapa-nombre').text.strip(),
                    'estado': etapa.select_one('.etapa-estado').text.strip(),
                    'fecha_inicio': etapa.select_one('.etapa-inicio').text.strip(),
                    'fecha_fin': etapa.select_one('.etapa-fin').text.strip()
                })
            except (AttributeError, KeyError):
                continue
                
        return etapas
    
    def _parsear_items(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los items del proceso"""
        items = []
        
        for item in soup.select('.item'):
            try:
                items.append({
                    'codigo': item.select_one('.item-codigo').text.strip(),
                    'descripcion': item.select_one('.item-descripcion').text.strip(),
                    'cantidad': item.select_one('.item-cantidad').text.strip(),
                    'unidad': item.select_one('.item-unidad').text.strip(),
                    'precio_unitario': item.select_one('.item-precio').text.strip()
                })
            except (AttributeError, KeyError):
                continue
                
        return items
    
    def _parsear_documentos(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los documentos del proceso"""
        documentos = []
        
        for doc in soup.select('.documento'):
            try:
                documentos.append({
                    'nombre': doc.select_one('.doc-nombre').text.strip(),
                    'tipo': doc.select_one('.doc-tipo').text.strip(),
                    'fecha': doc.select_one('.doc-fecha').text.strip(),
                    'tamaño': doc.select_one('.doc-size').text.strip(),
                    'url': doc.select_one('a')['href']
                })
            except (AttributeError, KeyError):
                continue
                
        return documentos
