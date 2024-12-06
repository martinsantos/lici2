import os
import unittest
import tempfile

from config.scraper_config import ScraperConfigManager, ScraperConfig

class TestScraperConfig(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial de pruebas
        """
        # Usar directorio temporal para configuraciones
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ScraperConfigManager(self.temp_dir)

    def test_crear_configuracion(self):
        """
        Probar creación de configuración
        """
        config = self.config_manager.crear_configuracion(
            nombre='Comprar Argentina',
            url_base='https://comprar.gob.ar',
            max_paginas=10,
            intervalo_solicitudes=2.0,
            filtros={
                'estado': 'En Proceso',
                'monto_minimo': 1000
            }
        )

        # Verificaciones
        self.assertIsNotNone(config)
        self.assertEqual(config.nombre, 'Comprar Argentina')
        self.assertEqual(config.url_base, 'https://comprar.gob.ar')
        self.assertEqual(config.max_paginas, 10)

    def test_cargar_configuracion(self):
        """
        Probar carga de configuración
        """
        # Crear configuración inicial
        config_original = self.config_manager.crear_configuracion(
            nombre='Argentina Compra',
            url_base='https://www.argentina.gob.ar/compras'
        )

        # Cargar configuración
        config_cargada = self.config_manager.cargar_configuracion('Argentina Compra')

        # Verificaciones
        self.assertIsNotNone(config_cargada)
        self.assertEqual(config_original.nombre, config_cargada.nombre)
        self.assertEqual(config_original.url_base, config_cargada.url_base)

    def test_actualizar_configuracion(self):
        """
        Probar actualización de configuración
        """
        # Crear configuración inicial
        self.config_manager.crear_configuracion(
            nombre='Boletín Oficial',
            url_base='https://www.boletinoficial.gob.ar'
        )

        # Actualizar configuración
        config_actualizada = self.config_manager.actualizar_configuracion(
            'Boletín Oficial',
            max_paginas=15,
            usar_proxy=False
        )

        # Verificaciones
        self.assertIsNotNone(config_actualizada)
        self.assertEqual(config_actualizada.max_paginas, 15)
        self.assertFalse(config_actualizada.usar_proxy)

    def test_listar_configuraciones(self):
        """
        Probar listado de configuraciones
        """
        # Crear múltiples configuraciones
        configs = [
            ('Comprar Argentina', 'https://comprar.gob.ar'),
            ('Argentina Compra', 'https://www.argentina.gob.ar/compras'),
            ('Boletín Oficial', 'https://www.boletinoficial.gob.ar')
        ]

        for nombre, url in configs:
            self.config_manager.crear_configuracion(nombre=nombre, url_base=url)

        # Listar configuraciones
        lista_configs = self.config_manager.listar_configuraciones()

        # Verificaciones
        self.assertGreater(len(lista_configs), 0)
        for nombre, _ in configs:
            self.assertIn(nombre.lower().replace(' ', '_'), lista_configs)

    def test_eliminar_configuracion(self):
        """
        Probar eliminación de configuración
        """
        # Crear configuración
        self.config_manager.crear_configuracion(
            nombre='Mercado Público',
            url_base='https://www.mercadopublico.cl'
        )

        # Eliminar configuración
        resultado = self.config_manager.eliminar_configuracion('Mercado Público')

        # Verificaciones
        self.assertTrue(resultado)
        
        # Intentar cargar configuración eliminada
        config_eliminada = self.config_manager.cargar_configuracion('Mercado Público')
        self.assertIsNone(config_eliminada)

def main():
    """
    Ejecutar pruebas de configuración
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScraperConfig)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Salir con código de error si hay pruebas fallidas
    import sys
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
