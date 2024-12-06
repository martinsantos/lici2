import random
import requests
from typing import List, Optional, Dict
import logging
from requests.exceptions import RequestException

from ..logging_config import get_logger

class RequestManager:
    """
    Gestiona solicitudes HTTP con rotación de User-Agents y soporte de proxies
    """
    def __init__(
        self, 
        proxies: List[str] = None, 
        user_agents: List[str] = None,
        logger=None
    ):
        """
        Inicializar RequestManager
        
        Args:
            proxies (List[str], optional): Lista de proxies para rotación
            user_agents (List[str], optional): Lista de User-Agents para rotación
            logger (logging.Logger, optional): Logger personalizado
        """
        self.logger = logger or get_logger(self.__class__.__name__)
        
        # User-Agents por defecto si no se proporcionan
        self.user_agents = user_agents or [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Proxies por defecto si no se proporcionan
        self.proxies = proxies or []
        
        # Sesión de requests para mantener conexiones persistentes
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self):
        """
        Configurar sesión de requests con headers por defecto
        """
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get(
        self, 
        url: str, 
        timeout: int = 10, 
        allow_redirects: bool = True,
        verify: bool = True
    ) -> Optional[requests.Response]:
        """
        Realizar solicitud GET con rotación de User-Agent y proxy
        
        Args:
            url (str): URL a solicitar
            timeout (int, optional): Tiempo máximo de espera. Por defecto 10 segundos.
            allow_redirects (bool, optional): Permitir redirecciones. Por defecto True.
            verify (bool, optional): Verificar certificado SSL. Por defecto True.
        
        Returns:
            Optional[requests.Response]: Respuesta de la solicitud o None si falla
        """
        try:
            # Rotar User-Agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            
            # Configurar proxy si está disponible
            proxy = None
            if self.proxies:
                proxy = random.choice(self.proxies)
                proxy_dict = {
                    'http': proxy,
                    'https': proxy
                }
            else:
                proxy_dict = None
            
            # Realizar solicitud
            response = self.session.get(
                url, 
                timeout=timeout, 
                allow_redirects=allow_redirects,
                verify=verify,
                proxies=proxy_dict
            )
            
            # Verificar estado de la respuesta
            response.raise_for_status()
            
            return response
        
        except RequestException as e:
            self.logger.error(f"Error en solicitud a {url}: {e}")
            
            # Intentar con otro proxy si está disponible
            if proxy and len(self.proxies) > 1:
                self.proxies.remove(proxy)
                self.logger.warning(f"Proxy {proxy} removido. Quedan {len(self.proxies)} proxies.")
            
            return None

    def add_proxies(self, proxies: List[str]):
        """
        Añadir proxies a la lista de rotación
        
        Args:
            proxies (List[str]): Lista de proxies a añadir
        """
        self.proxies.extend(proxies)
        self.logger.info(f"Añadidos {len(proxies)} proxies. Total: {len(self.proxies)}")

    def get_proxy_list(self) -> List[str]:
        """
        Obtener lista de proxies disponibles
        
        Returns:
            List[str]: Lista de proxies
        """
        return self.proxies.copy()

# Función para obtener proxies gratuitos (ejemplo básico)
def fetch_free_proxies(max_proxies: int = 10) -> List[str]:
    """
    Obtener una lista de proxies gratuitos
    
    Args:
        max_proxies (int, optional): Número máximo de proxies a obtener. Por defecto 10.
    
    Returns:
        List[str]: Lista de proxies en formato 'ip:puerto'
    """
    logger = get_logger('ProxyFetcher')
    
    # URLs de servicios de proxies gratuitos (ejemplo)
    proxy_urls = [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'https://www.proxy-list.download/api/v1/get?type=http'
    ]
    
    proxies = []
    
    for url in proxy_urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parsear respuesta según el formato del servicio
            nuevos_proxies = response.text.strip().split('\n')
            
            # Filtrar y formatear proxies
            nuevos_proxies = [
                proxy.strip() for proxy in nuevos_proxies 
                if proxy.strip() and ':' in proxy.strip()
            ]
            
            proxies.extend(nuevos_proxies)
            
            # Detener si se alcanza el límite
            if len(proxies) >= max_proxies:
                break
        
        except Exception as e:
            logger.warning(f"Error obteniendo proxies de {url}: {e}")
    
    return proxies[:max_proxies]
