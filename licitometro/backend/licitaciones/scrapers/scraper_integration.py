import sys
import os
from typing import List, Dict, Type

# Añadir directorios padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from templates.base_template import BaseLicitacionTemplate
from scrapers.scraper_enhancer import enrich_licitaciones, ScraperEnhancer
from ..logging_config import get_logger
from ..config.scraper_config import obtener_config_manager, ScraperConfig
from ..notifications.notificador import obtener_notificador

class ScraperIntegration:
    def __init__(self, logger=None, config_manager=None, notificador=None):
        """
        Inicializar integración de scrapers con estrategias de enriquecimiento y notificaciones
        
        Args:
            logger (logging.Logger, optional): Logger personalizado
            config_manager (ScraperConfigManager, optional): Gestor de configuración
            notificador (Notificador, optional): Sistema de notificaciones
        """
        self.logger = logger or get_logger(__name__)
        self.config_manager = config_manager or obtener_config_manager()
        self.notificador = notificador or obtener_notificador()
        self.enhancer = ScraperEnhancer()

    def process_template_licitaciones(
        self, 
        template_class: Type[BaseLicitacionTemplate], 
        url: str
    ) -> List[Dict]:
        """
        Procesar licitaciones de un template específico con enriquecimiento
        
        Args:
            template_class (Type[BaseLicitacionTemplate]): Clase del template a usar
            url (str): URL de scraping
        
        Returns:
            List[Dict]: Lista de licitaciones enriquecidas
        """
        try:
            # Cargar configuración para el template
            config = self.config_manager.cargar_configuracion(template_class.__name__)
            
            # Si no hay configuración, usar valores por defecto
            if config is None:
                config = ScraperConfig(
                    nombre=template_class.__name__,
                    url_base=url
                )
                self.logger.warning(f"No se encontró configuración para {template_class.__name__}. Usando configuración por defecto.")
            
            # Instanciar template
            template_instance = template_class(url)
            
            # Extraer licitaciones originales
            raw_licitaciones = template_instance.extract_licitaciones()
            
            self.logger.info(f"Extraídas {len(raw_licitaciones)} licitaciones de {url}")
            
            # Aplicar filtros de configuración si existen
            if config.filtros:
                raw_licitaciones = self._aplicar_filtros(raw_licitaciones, config.filtros)
            
            # Enriquecer licitaciones
            enriched_licitaciones = []
            for licitacion in raw_licitaciones:
                resultado = self.enhancer.enrich_licitacion(licitacion)
                
                if resultado['is_valid']:
                    enriched_licitaciones.append(resultado['licitacion'])
                else:
                    self.logger.warning(f"Licitación inválida: {resultado['warnings']}")
            
            self.logger.info(f"Enriquecidas {len(enriched_licitaciones)} licitaciones")
            
            return enriched_licitaciones
        
        except Exception as e:
            self.logger.error(f"Error procesando template {template_class.__name__}: {str(e)}")
            return []

    def _aplicar_filtros(self, licitaciones: List[Dict], filtros: Dict) -> List[Dict]:
        """
        Aplicar filtros a las licitaciones
        
        Args:
            licitaciones (List[Dict]): Lista de licitaciones
            filtros (Dict): Diccionario de filtros
        
        Returns:
            List[Dict]: Lista de licitaciones filtradas
        """
        licitaciones_filtradas = []
        
        for licitacion in licitaciones:
            cumple_filtros = True
            
            for campo, valor in filtros.items():
                if campo not in licitacion:
                    cumple_filtros = False
                    break
                
                # Comparación de valores
                if isinstance(valor, (int, float)):
                    # Comparación numérica
                    if licitacion[campo] < valor:
                        cumple_filtros = False
                        break
                elif isinstance(valor, str):
                    # Comparación de cadenas
                    if valor.lower() not in licitacion[campo].lower():
                        cumple_filtros = False
                        break
            
            if cumple_filtros:
                licitaciones_filtradas.append(licitacion)
        
        return licitaciones_filtradas

    def batch_process_templates(
        self, 
        template_classes: List[Type[BaseLicitacionTemplate]], 
        urls: List[str],
        notificar: bool = True
    ) -> Dict:
        """
        Procesar múltiples templates de scraping con notificación opcional
        
        Args:
            template_classes (List[Type[BaseLicitacionTemplate]]): Clases de templates
            urls (List[str]): URLs a scrapear
            notificar (bool, optional): Habilitar notificaciones. Por defecto True.
        
        Returns:
            Dict: Resumen de procesamiento y notificaciones
        """
        # Procesar templates
        todas_licitaciones = []
        for template_class, url in zip(template_classes, urls):
            licitaciones = self.process_template_licitaciones(template_class, url)
            todas_licitaciones.extend(licitaciones)

        # Resumen de procesamiento
        resumen = {
            'total_licitaciones': len(todas_licitaciones),
            'templates_procesados': len(template_classes)
        }

        # Notificaciones
        if notificar and todas_licitaciones:
            try:
                resumen['notificaciones'] = self.notificador.notificar_nuevas_licitaciones(
                    todas_licitaciones
                )
            except Exception as e:
                self.logger.error(f"Error en notificaciones: {e}")
                resumen['notificaciones'] = None

        return resumen

    def validate_licitaciones_batch(self, licitaciones: List[Dict]) -> Dict:
        """
        Validación por lotes de licitaciones
        """
        validation_results = {
            'total': len(licitaciones),
            'valid': 0,
            'invalid': 0,
            'warnings': []
        }

        for licitacion in licitaciones:
            validation = self.enhancer._validate_licitacion(licitacion)
            
            if validation['is_valid']:
                validation_results['valid'] += 1
            else:
                validation_results['invalid'] += 1
                validation_results['warnings'].extend(validation['warnings'])

        validation_results['valid_percentage'] = (
            validation_results['valid'] / validation_results['total'] * 100 
            if validation_results['total'] > 0 else 0
        )

        return validation_results

# Ejemplo de uso y pruebas
def test_scraper_integration():
    """
    Función de prueba para integración de scrapers
    """
    from templates.comprar_template import ComprarTemplate  # Importar templates específicos
    from templates.argentina_compra_template import ArgentinaCompraTemplate

    # Configurar logging
    logger = get_logger('ScraperIntegrationTest')

    # Crear instancia de integración
    integrador = ScraperIntegration(logger)

    # URLs de ejemplo (reemplazar con URLs reales)
    urls_test = [
        'https://comprar.gob.ar/Compras.aspx',
        'https://www.argentinacompra.gov.ar/licitaciones'
    ]

    # Templates de ejemplo
    templates_test = [
        ComprarTemplate,
        ArgentinaCompraTemplate
    ]

    try:
        # Procesar lotes de licitaciones
        resultado = integrador.batch_process_templates(
            templates_test, 
            urls_test
        )

        logger.info("Resultados de Procesamiento:")
        logger.info(f"Licitaciones Procesadas: {resultado['total_licitaciones']}")
        logger.info(f"Templates Procesados: {resultado['templates_procesados']}")

        if resultado.get('notificaciones'):
            logger.info("Notificaciones Enviadas:")
            logger.info(resultado['notificaciones'])

        return resultado

    except Exception as e:
        logger.error(f"Error en prueba de integración: {str(e)}")
        return {}

if __name__ == "__main__":
    test_scraper_integration()
