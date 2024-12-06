import sys
import os
import unittest
from datetime import datetime, timedelta

# Añadir directorios padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.scraper_integration import ScraperIntegration
from templates.comprar_template import ComprarTemplate
from templates.argentina_compra_template import ArgentinaCompraTemplate
from templates.mercado_publico_template import MercadoPublicoTemplate
from logging_config import get_logger

class TestRealScraping(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial de pruebas de scraping real
        """
        self.logger = get_logger(self.__class__.__name__)
        self.integrador = ScraperIntegration(self.logger)

    def test_comprar_gob_ar_scraping(self):
        """
        Prueba de scraping en comprar.gob.ar
        """
        url_test = 'https://comprar.gob.ar/Compras.aspx'
        
        try:
            licitaciones = self.integrador.process_template_licitaciones(
                ComprarTemplate, 
                url_test
            )
            
            # Verificaciones básicas
            self.assertIsNotNone(licitaciones, "No se pudieron extraer licitaciones")
            self.assertGreater(len(licitaciones), 0, "No se encontraron licitaciones")
            
            # Verificar campos de cada licitación
            for licitacion in licitaciones:
                self._validate_licitacion(licitacion)
            
            self.logger.info(f"Extraídas {len(licitaciones)} licitaciones de {url_test}")
        
        except Exception as e:
            self.fail(f"Error en scraping de {url_test}: {e}")

    def test_argentina_compra_scraping(self):
        """
        Prueba de scraping en argentina.gob.ar/compras
        """
        url_test = 'https://www.argentina.gob.ar/compras/licitaciones-publicas'
        
        try:
            licitaciones = self.integrador.process_template_licitaciones(
                ArgentinaCompraTemplate, 
                url_test
            )
            
            # Verificaciones básicas
            self.assertIsNotNone(licitaciones, "No se pudieron extraer licitaciones")
            self.assertGreater(len(licitaciones), 0, "No se encontraron licitaciones")
            
            # Verificar campos de cada licitación
            for licitacion in licitaciones:
                self._validate_licitacion(licitacion)
            
            self.logger.info(f"Extraídas {len(licitaciones)} licitaciones de {url_test}")
        
        except Exception as e:
            self.fail(f"Error en scraping de {url_test}: {e}")

    def test_mercado_publico_scraping(self):
        """
        Prueba de scraping en Mercado Público
        """
        url_test = 'https://www.argentinacompra.gov.ar/licitaciones'
        
        try:
            licitaciones = self.integrador.process_template_licitaciones(
                MercadoPublicoTemplate, 
                url_test
            )
            
            # Verificaciones básicas
            self.assertIsNotNone(licitaciones, "No se pudieron extraer licitaciones")
            self.assertGreater(len(licitaciones), 0, "No se encontraron licitaciones")
            
            # Verificar campos de cada licitación
            for licitacion in licitaciones:
                self._validate_licitacion(licitacion)
            
            self.logger.info(f"Extraídas {len(licitaciones)} licitaciones de {url_test}")
        
        except Exception as e:
            self.fail(f"Error en scraping de {url_test}: {e}")

    def _validate_licitacion(self, licitacion: dict):
        """
        Validar campos de una licitación
        """
        # Verificar campos obligatorios
        campos_obligatorios = [
            'titulo', 
            'organismo', 
            'url_fuente', 
            'fecha_publicacion', 
            'estado'
        ]
        
        for campo in campos_obligatorios:
            self.assertIn(campo, licitacion, f"Falta campo {campo}")
            self.assertIsNotNone(licitacion[campo], f"Campo {campo} es None")
        
        # Validaciones específicas
        self.assertIsInstance(licitacion['titulo'], str, "Título debe ser string")
        self.assertIsInstance(licitacion['organismo'], str, "Organismo debe ser string")
        
        # Validar fecha de publicación
        self.assertIsInstance(licitacion['fecha_publicacion'], datetime, "Fecha debe ser datetime")
        self.assertTrue(
            licitacion['fecha_publicacion'] <= datetime.now(), 
            "Fecha de publicación no puede ser futura"
        )
        self.assertTrue(
            licitacion['fecha_publicacion'] > datetime.now() - timedelta(days=365), 
            "Fecha de publicación no puede ser de hace más de un año"
        )
        
        # Validar estado
        estados_validos = [
            'En Proceso', 'Publicado', 'Adjudicado', 
            'Cerrado', 'Finalizado'
        ]
        self.assertIn(licitacion['estado'], estados_validos, "Estado no válido")

def main():
    """
    Ejecutar pruebas de scraping real
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRealScraping)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Salir con código de error si hay pruebas fallidas
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
