import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class MendozaClient:
    """Cliente para los sistemas de compras de Mendoza"""
    
    COMPRAR_URL = "https://comprar.mendoza.gov.ar"
    COMPRAS_URL = "https://comprasapps.mendoza.gov.ar"
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def buscar_comprar_mendoza(
        self,
        query: str,
        max_results: int = 100,
        filtros: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca licitaciones en Comprar Mendoza
        
        Args:
            query: Términos de búsqueda
            max_results: Número máximo de resultados
            filtros: Filtros adicionales (opcional)
                - fecha_desde: Fecha inicio (DD/MM/YYYY)
                - fecha_hasta: Fecha fin (DD/MM/YYYY)
                - estado: Estado del proceso
                - organismo: Organismo comprador
                - tipo: Tipo de contratación
        
        Returns:
            Lista de licitaciones encontradas
        """
        try:
            # Primero necesitamos obtener un token de sesión
            async with self.session.get(f"{self.COMPRAR_URL}/Compras.aspx") as response:
                response.raise_for_status()
                html = await response.text()
                token = self._extraer_token_sesion(html)
            
            # Construir parámetros de búsqueda
            params = {
                '__VIEWSTATE': token,
                'txtBuscar': query,
                'ddlRegistros': min(max_results, 100),
                'btnBuscar': 'Buscar'
            }
            
            # Agregar filtros si existen
            if filtros:
                if 'fecha_desde' in filtros:
                    params['txtFechaDesde'] = filtros['fecha_desde']
                if 'fecha_hasta' in filtros:
                    params['txtFechaHasta'] = filtros['fecha_hasta']
                if 'estado' in filtros:
                    params['ddlEstado'] = filtros['estado']
                if 'organismo' in filtros:
                    params['ddlOrganismo'] = filtros['organismo']
                if 'tipo' in filtros:
                    params['ddlTipo'] = filtros['tipo']
            
            async with self.session.post(
                f"{self.COMPRAR_URL}/Compras.aspx",
                data=params
            ) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_resultados_comprar(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error en la búsqueda Comprar Mendoza: {str(e)}")
            raise
    
    def _extraer_token_sesion(self, html: str) -> str:
        """Extrae el token de sesión del formulario"""
        soup = BeautifulSoup(html, 'html.parser')
        token = soup.select_one('#__VIEWSTATE')
        if token:
            return token['value']
        raise ValueError("No se pudo obtener el token de sesión")
    
    def _parsear_resultados_comprar(self, html: str) -> List[Dict]:
        """Parsea los resultados de Comprar Mendoza"""
        soup = BeautifulSoup(html, 'html.parser')
        resultados = []
        
        for row in soup.select('.grid-row'):
            try:
                resultado = {
                    'numero': row.select_one('.numero-proceso').text.strip(),
                    'nombre': row.select_one('.nombre-proceso').text.strip(),
                    'organismo': row.select_one('.organismo').text.strip(),
                    'tipo': row.select_one('.tipo-contratacion').text.strip(),
                    'estado': row.select_one('.estado').text.strip(),
                    'fecha_publicacion': row.select_one('.fecha-pub').text.strip(),
                    'fecha_apertura': row.select_one('.fecha-apertura').text.strip(),
                    'monto_estimado': row.select_one('.monto').text.strip(),
                    'url': f"{self.COMPRAR_URL}{row.select_one('a')['href']}"
                }
                
                resultados.append(resultado)
                
            except (AttributeError, KeyError) as e:
                logger.warning(f"Error parseando resultado Comprar: {str(e)}")
                continue
        
        return resultados
    
    async def buscar_compras_mendoza(
        self,
        query: str,
        max_results: int = 100,
        filtros: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca licitaciones en Compras Mendoza (portal legacy)
        
        Args:
            query: Términos de búsqueda
            max_results: Número máximo de resultados
            filtros: Filtros adicionales (opcional)
                - fecha_desde: Fecha inicio (YYYY-MM-DD)
                - fecha_hasta: Fecha fin (YYYY-MM-DD)
                - estado: Estado del proceso
                - reparticion: Repartición compradora
        
        Returns:
            Lista de licitaciones encontradas
        """
        try:
            params = {
                'accion': 'buscar',
                'texto': query,
                'limite': min(max_results, 100),
                'pagina': 1
            }
            
            # Agregar filtros si existen
            if filtros:
                if 'fecha_desde' in filtros:
                    params['fecha_desde'] = filtros['fecha_desde']
                if 'fecha_hasta' in filtros:
                    params['fecha_hasta'] = filtros['fecha_hasta']
                if 'estado' in filtros:
                    params['estado'] = filtros['estado']
                if 'reparticion' in filtros:
                    params['reparticion'] = filtros['reparticion']
            
            async with self.session.get(
                f"{self.COMPRAS_URL}/Compras/servlet/hli00049",
                params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return self._parsear_resultados_compras(data)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error en la búsqueda Compras Mendoza: {str(e)}")
            raise
    
    def _parsear_resultados_compras(self, data: Dict) -> List[Dict]:
        """Parsea los resultados de Compras Mendoza"""
        resultados = []
        
        for item in data.get('items', []):
            try:
                resultado = {
                    'numero_expediente': item['nro_expediente'],
                    'nombre': item['descripcion'],
                    'reparticion': item['reparticion'],
                    'tipo': item['tipo_contratacion'],
                    'estado': item['estado'],
                    'fecha_publicacion': item['fecha_publicacion'],
                    'fecha_apertura': item['fecha_apertura'],
                    'presupuesto': item['presupuesto_oficial'],
                    'url': f"{self.COMPRAS_URL}/expediente/{item['id']}"
                }
                
                resultados.append(resultado)
                
            except KeyError as e:
                logger.warning(f"Error parseando resultado Compras: {str(e)}")
                continue
        
        return resultados
    
    async def obtener_detalle_comprar(self, proceso_id: str) -> Dict:
        """
        Obtiene el detalle de un proceso en Comprar Mendoza
        
        Args:
            proceso_id: ID del proceso
            
        Returns:
            Detalles del proceso
        """
        try:
            url = f"{self.COMPRAR_URL}/Proceso.aspx?id={proceso_id}"
            
            async with self.session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                
                return self._parsear_detalle_comprar(html)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error obteniendo detalle Comprar: {str(e)}")
            raise
    
    def _parsear_detalle_comprar(self, html: str) -> Dict:
        """Parsea los detalles de un proceso en Comprar"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            detalle = {
                'numero_proceso': soup.select_one('.proceso-numero').text.strip(),
                'nombre': soup.select_one('.proceso-nombre').text.strip(),
                'descripcion': soup.select_one('.descripcion').text.strip(),
                'organismo': soup.select_one('.organismo-nombre').text.strip(),
                'tipo_contratacion': soup.select_one('.tipo').text.strip(),
                'estado': soup.select_one('.estado').text.strip(),
                'moneda': soup.select_one('.moneda').text.strip(),
                'monto_estimado': soup.select_one('.monto').text.strip(),
                'fechas': {
                    'publicacion': soup.select_one('.fecha-publicacion').text.strip(),
                    'apertura': soup.select_one('.fecha-apertura').text.strip(),
                    'visita': soup.select_one('.fecha-visita').text.strip()
                },
                'items': self._parsear_items_comprar(soup),
                'documentos': self._parsear_documentos_comprar(soup)
            }
            
            return detalle
            
        except (AttributeError, KeyError) as e:
            logger.error(f"Error parseando detalle Comprar: {str(e)}")
            raise
    
    def _parsear_items_comprar(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los items del proceso en Comprar"""
        items = []
        
        for item in soup.select('.item-detalle'):
            try:
                items.append({
                    'codigo': item.select_one('.codigo').text.strip(),
                    'descripcion': item.select_one('.descripcion').text.strip(),
                    'cantidad': item.select_one('.cantidad').text.strip(),
                    'unidad': item.select_one('.unidad').text.strip(),
                    'precio_estimado': item.select_one('.precio').text.strip()
                })
            except (AttributeError, KeyError):
                continue
                
        return items
    
    def _parsear_documentos_comprar(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los documentos del proceso en Comprar"""
        documentos = []
        
        for doc in soup.select('.documento'):
            try:
                documentos.append({
                    'nombre': doc.select_one('.nombre').text.strip(),
                    'tipo': doc.select_one('.tipo').text.strip(),
                    'fecha': doc.select_one('.fecha').text.strip(),
                    'tamaño': doc.select_one('.size').text.strip(),
                    'url': doc.select_one('a')['href']
                })
            except (AttributeError, KeyError):
                continue
                
        return documentos
    
    async def obtener_detalle_compras(self, expediente_id: str) -> Dict:
        """
        Obtiene el detalle de un expediente en Compras Mendoza
        
        Args:
            expediente_id: ID del expediente
            
        Returns:
            Detalles del expediente
        """
        try:
            url = f"{self.COMPRAS_URL}/Compras/servlet/hli00050"
            params = {'id': expediente_id}
            
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                return self._parsear_detalle_compras(data)
                
        except aiohttp.ClientError as e:
            logger.error(f"Error obteniendo detalle Compras: {str(e)}")
            raise
    
    def _parsear_detalle_compras(self, data: Dict) -> Dict:
        """Parsea los detalles de un expediente en Compras"""
        try:
            detalle = {
                'numero_expediente': data['nro_expediente'],
                'caratula': data['caratula'],
                'descripcion': data['descripcion'],
                'reparticion': {
                    'nombre': data['reparticion'],
                    'direccion': data['direccion'],
                    'telefono': data['telefono']
                },
                'tipo_contratacion': data['tipo_contratacion'],
                'estado': data['estado'],
                'presupuesto': {
                    'moneda': data['moneda'],
                    'monto': data['presupuesto_oficial']
                },
                'fechas': {
                    'publicacion': data['fecha_publicacion'],
                    'apertura': data['fecha_apertura'],
                    'preadjudicacion': data.get('fecha_preadjudicacion'),
                    'adjudicacion': data.get('fecha_adjudicacion')
                },
                'items': [
                    {
                        'codigo': item['codigo'],
                        'descripcion': item['descripcion'],
                        'cantidad': item['cantidad'],
                        'unidad': item['unidad_medida'],
                        'precio_estimado': item['precio_unitario']
                    }
                    for item in data.get('items', [])
                ],
                'documentos': [
                    {
                        'nombre': doc['nombre'],
                        'tipo': doc['tipo'],
                        'fecha': doc['fecha'],
                        'url': f"{self.COMPRAS_URL}/documentos/{doc['id']}"
                    }
                    for doc in data.get('documentos', [])
                ]
            }
            
            return detalle
            
        except KeyError as e:
            logger.error(f"Error parseando detalle Compras: {str(e)}")
            raise
