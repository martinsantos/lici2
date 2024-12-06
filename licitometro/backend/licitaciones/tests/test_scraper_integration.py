import unittest
import sys
import os
import logging

# Añadir directorios padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.scraper_integration import ScraperIntegration
from templates.base_template import BaseLicitacionTemplate

class MockTemplate(BaseLicitacionTemplate):
    """
    Template de prueba para validar integración de scrapers
    """
    def __init__(self, url: str):
        super().__init__(url)
        self._test_licitaciones = [
            {
                'titulo': 'Licitación de Prueba 1',
                'organismo': 'Organismo Test 1',
                'url_fuente': 'https://ejemplo.com/licitacion1'
            },
            {
                'titulo': 'Licitación de Prueba 2',
                'url_fuente': 'https://ejemplo.com/licitacion2'
            },
            {
                'organismo': 'Organismo Test 3',
                'url_fuente': 'https://ejemplo.com/licitacion3'
            }
        ]

    def extract_licitaciones(self) -> List[Dict]:
        """
        Método de extracción de prueba
        """
        return self._test_licitaciones

class TestScraperIntegration(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial de pruebas
        """
        logging.basicConfig(level=logging.INFO)
        self.integrador = ScraperIntegration()

    def test_process_template_licitaciones(self):
        """
        Probar procesamiento de licitaciones de un template
        """
        url_test = 'https://ejemplo.com/test'
        licitaciones = self.integrador.process_template_licitaciones(MockTemplate, url_test)
        
        # Verificar que se procesaron licitaciones
        self.assertGreater(len(licitaciones), 0, "No se procesaron licitaciones")
        
        # Verificar campos enriquecidos
        for licitacion in licitaciones:
            self.assertIn('titulo', licitacion, "Falta campo título")
            self.assertIn('organismo', licitacion, "Falta campo organismo")
            self.assertIn('estado', licitacion, "Falta campo estado")
            self.assertIn('fecha_publicacion', licitacion, "Falta campo fecha de publicación")

    def test_batch_process_templates(self):
        """
        Probar procesamiento por lotes de múltiples templates
        """
        templates = [MockTemplate, MockTemplate]
        urls = ['https://ejemplo.com/test1', 'https://ejemplo.com/test2']
        
        licitaciones = self.integrador.batch_process_templates(templates, urls)
        
        # Verificar procesamiento de múltiples templates
        self.assertGreater(len(licitaciones), 0, "No se procesaron licitaciones en lote")

    def test_validate_licitaciones_batch(self):
        """
        Probar validación por lotes de licitaciones
        """
        url_test = 'https://ejemplo.com/test'
        licitaciones = self.integrador.process_template_licitaciones(MockTemplate, url_test)
        
        validacion = self.integrador.validate_licitaciones_batch(licitaciones)
        
        # Verificar métricas de validación
        self.assertIn('total', validacion)
        self.assertIn('valid', validacion)
        self.assertIn('invalid', validacion)
        self.assertIn('valid_percentage', validacion)
        
        # Verificar coherencia de métricas
        self.assertEqual(
            validacion['total'], 
            validacion['valid'] + validacion['invalid'], 
            "Métricas de validación inconsistentes"
        )

def main():
    """
    Ejecutar pruebas de integración
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScraperIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Salir con código de error si hay pruebas fallidas
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
