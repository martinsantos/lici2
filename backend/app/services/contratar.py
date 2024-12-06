import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContratarClient:
    """Cliente para el sistema CONTRAT.AR de Argentina"""
    
    BASE_URL = "https://contratar.gob.ar"
    SEARCH_URL = f"{BASE_URL}/obras-publicas"
    
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
        Busca licitaciones de obra pública en CONTRAT.AR
        
        Args:
            query: Términos de búsqueda
            max_results: Número máximo de resultados
            filtros: Filtros adicionales (opcional)
                - fecha_desde: Fecha inicio (YYYY-MM-DD)
                - fecha_hasta: Fecha fin (YYYY-MM-DD)
                - estado: Estado de la obra
                - provincia: Provincia de la obra
                - tipo_obra: Tipo de obra
        
        Returns:
            Lista de licitaciones encontradas
        """
        try:
            params = {
                'searchText': query,
                'limit': min(max_results, 100),
                'offset': 0
            }
            
            # Agregar filtros si existen
            if filtros:
                if 'fecha_desde' in filtros:
                    params['startDate'] = filtros['fecha_desde']
                if 'fecha_hasta' in filtros:
                    params['endDate'] = filtros['fecha_hasta']
                if 'estado' in filtros:
                    params['status'] = filtros['estado']
                if 'provincia' in filtros:
                    params['province'] = filtros['provincia']
                if 'tipo_obra' in filtros:
                    params['workType'] = filtros['tipo_obra']
            
            async with self.session.get(
                self.SEARCH_URL,
                params=params
            ) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_resultados(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error en la búsqueda CONTRAT.AR: {str(e)}")
            raise
    
    def _parsear_resultados(self, html: str) -> List[Dict]:
        """Parsea los resultados de la búsqueda"""
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []
        
        for item in soup.select('.public-work-item'):
            try:
                resultado = {
                    'id': item.get('data-work-id'),
                    'titulo': item.select_one('.work-title').text.strip(),
                    'organismo': item.select_one('.contracting-agency').text.strip(),
                    'tipo_obra': item.select_one('.work-type').text.strip(),
                    'estado': item.select_one('.work-status').text.strip(),
                    'provincia': item.select_one('.province').text.strip(),
                    'localidad': item.select_one('.locality').text.strip(),
                    'fecha_publicacion': item.select_one('.publish-date').text.strip(),
                    'fecha_apertura': item.select_one('.opening-date').text.strip(),
                    'presupuesto': item.select_one('.budget').text.strip(),
                    'plazo_meses': item.select_one('.term-months').text.strip(),
                    'url': f"{self.BASE_URL}{item.select_one('a')['href']}"
                }
                
                resultados.append(resultado)
                
            except (AttributeError, KeyError) as e:
                logger.warning(f"Error parseando resultado: {str(e)}")
                continue
        
        return resultados
    
    async def obtener_detalle(self, obra_id: str) -> Dict:
        """
        Obtiene el detalle de una obra pública específica
        
        Args:
            obra_id: ID de la obra
            
        Returns:
            Detalles de la obra
        """
        try:
            url = f"{self.BASE_URL}/obra/{obra_id}"
            
            async with self.session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_detalle(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error obteniendo detalle: {str(e)}")
            raise
    
    def _parsear_detalle(self, html: str) -> Dict:
        """Parsea los detalles de una obra"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            detalle = {
                'numero_proceso': soup.select_one('.process-number').text.strip(),
                'nombre': soup.select_one('.work-name').text.strip(),
                'descripcion': soup.select_one('.description').text.strip(),
                'organismo': soup.select_one('.agency-details').text.strip(),
                'tipo_obra': soup.select_one('.work-type').text.strip(),
                'estado': soup.select_one('.status').text.strip(),
                'ubicacion': {
                    'provincia': soup.select_one('.province').text.strip(),
                    'localidad': soup.select_one('.locality').text.strip(),
                    'direccion': soup.select_one('.address').text.strip(),
                    'coordenadas': {
                        'lat': soup.select_one('.latitude')['value'],
                        'lon': soup.select_one('.longitude')['value']
                    }
                },
                'presupuesto': {
                    'moneda': soup.select_one('.currency').text.strip(),
                    'monto': soup.select_one('.amount').text.strip()
                },
                'plazos': {
                    'ejecucion_meses': soup.select_one('.execution-term').text.strip(),
                    'garantia_meses': soup.select_one('.warranty-term').text.strip()
                },
                'fechas': {
                    'publicacion': soup.select_one('.publish-date').text.strip(),
                    'visita_obra': soup.select_one('.visit-date').text.strip(),
                    'apertura': soup.select_one('.opening-date').text.strip()
                },
                'requisitos': self._parsear_requisitos(soup),
                'documentos': self._parsear_documentos(soup)
            }
            
            return detalle
            
        except (AttributeError, KeyError) as e:
            logger.error(f"Error parseando detalle: {str(e)}")
            raise
    
    def _parsear_requisitos(self, soup: BeautifulSoup) -> Dict:
        """Parsea los requisitos de la obra"""
        try:
            return {
                'capacidad_tecnica': soup.select_one('.technical-capacity').text.strip(),
                'capacidad_financiera': soup.select_one('.financial-capacity').text.strip(),
                'registro_constructores': soup.select_one('.builders-registry').text.strip(),
                'certificaciones': [
                    cert.text.strip()
                    for cert in soup.select('.required-certifications li')
                ]
            }
        except (AttributeError, KeyError):
            return {}
    
    def _parsear_documentos(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los documentos adjuntos"""
        documentos = []
        
        for doc in soup.select('.document-item'):
            try:
                documentos.append({
                    'nombre': doc.select_one('.doc-name').text.strip(),
                    'tipo': doc.select_one('.doc-type').text.strip(),
                    'fecha': doc.select_one('.doc-date').text.strip(),
                    'tamaño': doc.select_one('.doc-size').text.strip(),
                    'url': doc.select_one('a')['href']
                })
            except (AttributeError, KeyError):
                continue
                
        return documentos
