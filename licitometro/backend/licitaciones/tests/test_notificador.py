import os
import unittest
from unittest.mock import patch, MagicMock

from ..notifications.notificador import Notificador

class TestNotificador(unittest.TestCase):
    def setUp(self):
        # Configuración de prueba
        self.config_test_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'configs', 
            'test_notificaciones_config.json'
        )
        
        # Crear configuración de prueba
        self.config_test = {
            'email': {
                'habilitado': True,
                'smtp_host': 'smtp.test.com',
                'smtp_puerto': 587,
                'remitente': 'test@example.com',
                'password': 'test_password',
                'destinatarios': ['dest1@example.com', 'dest2@example.com']
            },
            'telegram': {
                'habilitado': True,
                'token_bot': 'test_token',
                'chat_ids': ['123456', '789012']
            },
            'webhook': {
                'habilitado': True,
                'urls': ['https://test.webhook.com/notify']
            },
            'filtros': {
                'monto_minimo': 1000,
                'estados': ['En Proceso'],
                'organismos': ['Ministerio de Obras Públicas']
            }
        }
        
        # Inicializar notificador con configuración de prueba
        self.notificador = Notificador(config_path=self.config_test_path)
        self.notificador.config = self.config_test

    def test_cargar_configuracion(self):
        """
        Probar carga de configuración
        """
        # Verificar que la configuración se cargue correctamente
        self.assertIsNotNone(self.notificador.config)
        self.assertTrue(self.notificador.config['email']['habilitado'])
        self.assertTrue(self.notificador.config['telegram']['habilitado'])

    def test_filtrar_licitaciones(self):
        """
        Probar filtrado de licitaciones
        """
        licitaciones_test = [
            {
                'titulo': 'Licitación 1',
                'monto': 500,
                'estado': 'Pendiente',
                'organismo': 'Otro Ministerio'
            },
            {
                'titulo': 'Licitación 2',
                'monto': 2000,
                'estado': 'En Proceso',
                'organismo': 'Ministerio de Obras Públicas'
            }
        ]

        # Filtrar licitaciones
        licitaciones_filtradas = self.notificador._filtrar_licitaciones(licitaciones_test)
        
        # Verificar que solo se incluya la segunda licitación
        self.assertEqual(len(licitaciones_filtradas), 1)
        self.assertEqual(licitaciones_filtradas[0]['titulo'], 'Licitación 2')

    @patch('smtplib.SMTP')
    def test_notificar_por_email(self, mock_smtp):
        """
        Probar notificación por email
        """
        licitaciones_test = [
            {
                'titulo': 'Licitación de Prueba',
                'monto': 5000,
                'estado': 'En Proceso',
                'organismo': 'Ministerio de Obras Públicas',
                'url_fuente': 'https://test.com/licitacion'
            }
        ]

        # Simular envío de email
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Enviar notificaciones
        emails_enviados = self.notificador._notificar_por_email(licitaciones_test)
        
        # Verificar que se enviaron emails
        self.assertEqual(emails_enviados, 2)
        self.assertEqual(mock_server.sendmail.call_count, 2)

    @patch('requests.post')
    def test_notificar_por_telegram(self, mock_post):
        """
        Probar notificación por Telegram
        """
        licitaciones_test = [
            {
                'titulo': 'Licitación de Prueba',
                'monto': 5000,
                'estado': 'En Proceso',
                'organismo': 'Ministerio de Obras Públicas',
                'url_fuente': 'https://test.com/licitacion'
            }
        ]

        # Simular respuesta de Telegram
        mock_post.return_value.status_code = 200

        # Enviar notificaciones
        mensajes_enviados = self.notificador._notificar_por_telegram(licitaciones_test)
        
        # Verificar que se enviaron mensajes
        self.assertEqual(mensajes_enviados, 2)
        self.assertEqual(mock_post.call_count, 2)

    @patch('requests.post')
    def test_notificar_por_webhook(self, mock_post):
        """
        Probar notificación por Webhook
        """
        licitaciones_test = [
            {
                'titulo': 'Licitación de Prueba',
                'monto': 5000,
                'estado': 'En Proceso',
                'organismo': 'Ministerio de Obras Públicas',
                'url_fuente': 'https://test.com/licitacion'
            }
        ]

        # Simular respuesta de Webhook
        mock_post.return_value.status_code = 200

        # Enviar notificaciones
        webhooks_invocados = self.notificador._notificar_por_webhook(licitaciones_test)
        
        # Verificar que se invocaron webhooks
        self.assertEqual(webhooks_invocados, 1)
        self.assertEqual(mock_post.call_count, 1)

    def test_notificar_nuevas_licitaciones(self):
        """
        Probar flujo completo de notificaciones
        """
        # Configurar mocks para cada método de notificación
        with patch.object(self.notificador, '_notificar_por_email', return_value=2) as mock_email, \
             patch.object(self.notificador, '_notificar_por_telegram', return_value=2) as mock_telegram, \
             patch.object(self.notificador, '_notificar_por_webhook', return_value=1) as mock_webhook:
            
            licitaciones_test = [
                {
                    'titulo': 'Licitación de Prueba',
                    'monto': 5000,
                    'estado': 'En Proceso',
                    'organismo': 'Ministerio de Obras Públicas',
                    'url_fuente': 'https://test.com/licitacion'
                }
            ]

            # Ejecutar notificación
            resumen = self.notificador.notificar_nuevas_licitaciones(licitaciones_test)

            # Verificar resumen de notificaciones
            self.assertEqual(resumen['total_licitaciones'], 1)
            self.assertEqual(resumen['licitaciones_filtradas'], 1)
            self.assertEqual(resumen['notificaciones_enviadas']['email'], 2)
            self.assertEqual(resumen['notificaciones_enviadas']['telegram'], 2)
            self.assertEqual(resumen['notificaciones_enviadas']['webhook'], 1)

if __name__ == '__main__':
    unittest.main()
