import sys
import os
import unittest
from datetime import datetime, timedelta
import json
from database.persistencia import obtener_persistencia

# Añadir directorios padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.scraper_integration import ScraperIntegration
from templates.comprar_template import ComprarTemplate
from templates.argentina_compra_template import ArgentinaCompraTemplate
from templates.mercado_publico_template import MercadoPublicoTemplate
from templates.boletin_oficial_template import BoletinOficialTemplate
from scrapers.scraper_enhancer import ScraperEnhancer
from logging_config import get_logger
from utils.request_manager import RequestManager, fetch_free_proxies

class TestFullIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Configuración inicial para pruebas de integración
        """
        cls.logger = get_logger(cls.__name__)
        cls.integrador = ScraperIntegration()
        cls.enhancer = ScraperEnhancer()
        cls.request_manager = RequestManager()

        # Obtener proxies gratuitos
        cls.proxies = fetch_free_proxies(max_proxies=5)
        cls.logger.info(f"Proxies obtenidos: {cls.proxies}")

    def test_full_scraping_workflow(self):
        """
        Prueba de flujo completo de scraping
        """
        # Templates y URLs a probar
        templates_urls = [
            (ComprarTemplate, 'https://comprar.gob.ar/Compras.aspx'),
            (ArgentinaCompraTemplate, 'https://www.argentina.gob.ar/compras/licitaciones-publicas'),
            (MercadoPublicoTemplate, 'https://www.argentinacompra.gov.ar/licitaciones'),
            (BoletinOficialTemplate, 'https://www.boletinoficial.gob.ar/seccion/licitaciones')
        ]

        # Resultados de scraping
        resultados_scraping = {}

        for template_class, url in templates_urls:
            try:
                # Extraer licitaciones
                licitaciones_raw = self.integrador.process_template_licitaciones(
                    template_class, 
                    url
                )

                # Enriquecer licitaciones
                licitaciones_enriquecidas = []
                for licitacion in licitaciones_raw:
                    resultado = self.enhancer.enrich_licitacion(licitacion)
                    if resultado['is_valid']:
                        licitaciones_enriquecidas.append(resultado['licitacion'])

                # Almacenar resultados
                resultados_scraping[template_class.__name__] = {
                    'total_extraidas': len(licitaciones_raw),
                    'total_enriquecidas': len(licitaciones_enriquecidas),
                    'licitaciones': licitaciones_enriquecidas
                }

                # Verificaciones
                self.assertGreater(
                    len(licitaciones_enriquecidas), 
                    0, 
                    f"No se enriquecieron licitaciones para {template_class.__name__}"
                )

            except Exception as e:
                self.logger.error(f"Error en scraping de {template_class.__name__}: {e}")
                self.fail(f"Fallo en scraping de {template_class.__name__}")

        # Guardar resultados para revisión manual
        self._guardar_resultados(resultados_scraping)

        # Métricas generales
        total_licitaciones = sum(
            res['total_enriquecidas'] for res in resultados_scraping.values()
        )
        self.logger.info(f"Total de licitaciones enriquecidas: {total_licitaciones}")

    def test_proxy_rotation(self):
        """
        Prueba de rotación de proxies
        """
        # Añadir proxies obtenidos
        self.request_manager.add_proxies(self.proxies)

        # Verificar que los proxies se añadieron correctamente
        proxies_actuales = self.request_manager.get_proxy_list()
        self.assertEqual(
            len(proxies_actuales), 
            len(self.proxies), 
            "No se añadieron correctamente los proxies"
        )

        # Probar solicitud con proxy
        url_test = 'https://httpbin.org/ip'
        try:
            response = self.request_manager.get(url_test)
            self.assertIsNotNone(response, "Fallo solicitud con proxy")
        except Exception as e:
            self.fail(f"Error en solicitud con proxy: {e}")

    def test_persistencia_licitaciones(self):
        """
        Prueba de persistencia de licitaciones
        """
        # Obtener persistencia
        persistencia = obtener_persistencia()

        # Templates y URLs a probar
        templates_urls = [
            (ComprarTemplate, 'https://comprar.gob.ar/Compras.aspx'),
            (ArgentinaCompraTemplate, 'https://www.argentina.gob.ar/compras/licitaciones-publicas'),
            (MercadoPublicoTemplate, 'https://www.argentinacompra.gov.ar/licitaciones'),
            (BoletinOficialTemplate, 'https://www.boletinoficial.gob.ar/seccion/licitaciones')
        ]

        # Total de licitaciones guardadas
        total_guardadas = 0

        # Iterar sobre templates
        for template_class, url in templates_urls:
            try:
                # Extraer y enriquecer licitaciones
                licitaciones_raw = self.integrador.process_template_licitaciones(
                    template_class, 
                    url
                )

                # Guardar licitaciones
                resultado_guardado = persistencia.guardar_licitaciones_batch(licitaciones_raw)
                
                # Verificaciones
                self.assertGreater(
                    resultado_guardado['guardadas'], 
                    0, 
                    f"No se guardaron licitaciones de {template_class.__name__}"
                )
                
                total_guardadas += resultado_guardado['guardadas']

            except Exception as e:
                self.logger.error(f"Error en persistencia de {template_class.__name__}: {e}")
                self.fail(f"Fallo en persistencia de {template_class.__name__}")

        # Verificar búsqueda de licitaciones
        licitaciones_encontradas = persistencia.buscar_licitaciones()
        self.assertGreater(
            len(licitaciones_encontradas), 
            0, 
            "No se encontraron licitaciones guardadas"
        )

        self.logger.info(f"Total de licitaciones guardadas: {total_guardadas}")
        self.logger.info(f"Total de licitaciones encontradas: {len(licitaciones_encontradas)}")

    def _guardar_resultados(self, resultados: dict):
        """
        Guardar resultados de scraping en archivo JSON
        """
        directorio_logs = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'logs'
        )
        os.makedirs(directorio_logs, exist_ok=True)

        nombre_archivo = os.path.join(
            directorio_logs, 
            f'resultados_scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )

        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(
                    resultados, 
                    f, 
                    ensure_ascii=False, 
                    indent=2,
                    default=str  # Manejar objetos no serializables
                )
            self.logger.info(f"Resultados guardados en {nombre_archivo}")
        except Exception as e:
            self.logger.error(f"Error guardando resultados: {e}")

def main():
    """
    Ejecutar pruebas de integración completas
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFullIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Salir con código de error si hay pruebas fallidas
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
