import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Union

from ..logging_config import get_logger
from ..database.persistencia import obtener_persistencia

class Notificador:
    """
    Sistema de notificaciones para nuevas licitaciones
    """
    def __init__(
        self, 
        config_path: str = None, 
        persistencia=None
    ):
        """
        Inicializar notificador
        
        Args:
            config_path (str, optional): Ruta al archivo de configuración de notificaciones
            persistencia (LicitacionesPersistencia, optional): Instancia de persistencia
        """
        self.logger = get_logger(self.__class__.__name__)
        self.persistencia = persistencia or obtener_persistencia()
        
        # Ruta de configuración por defecto
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'configs', 
                'notificaciones_config.json'
            )
        
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Cargar configuración
        self.config_path = config_path
        self.config = self._cargar_configuracion()

    def _cargar_configuracion(self) -> Dict:
        """
        Cargar configuración de notificaciones
        
        Returns:
            Dict: Configuración de notificaciones
        """
        config_defecto = {
            'email': {
                'habilitado': False,
                'smtp_host': '',
                'smtp_puerto': 587,
                'remitente': '',
                'password': '',
                'destinatarios': []
            },
            'telegram': {
                'habilitado': False,
                'token_bot': '',
                'chat_ids': []
            },
            'webhook': {
                'habilitado': False,
                'urls': []
            },
            'filtros': {
                'monto_minimo': 0,
                'estados': ['En Proceso', 'Publicado'],
                'organismos': []
            }
        }

        try:
            # Intentar cargar configuración existente
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_guardada = json.load(f)
                    # Combinar configuración guardada con valores por defecto
                    config_defecto.update(config_guardada)
            else:
                # Guardar configuración por defecto
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_defecto, f, indent=2)
            
            return config_defecto
        
        except Exception as e:
            self.logger.error(f"Error cargando configuración de notificaciones: {e}")
            return config_defecto

    def guardar_configuracion(self, nueva_config: Dict):
        """
        Guardar nueva configuración de notificaciones
        
        Args:
            nueva_config (Dict): Nueva configuración
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(nueva_config, f, indent=2)
            
            # Actualizar configuración en memoria
            self.config = nueva_config
            self.logger.info("Configuración de notificaciones actualizada")
        
        except Exception as e:
            self.logger.error(f"Error guardando configuración de notificaciones: {e}")

    def _filtrar_licitaciones(self, licitaciones: List[Dict]) -> List[Dict]:
        """
        Filtrar licitaciones según configuración
        
        Args:
            licitaciones (List[Dict]): Lista de licitaciones
        
        Returns:
            List[Dict]: Licitaciones filtradas
        """
        filtros = self.config.get('filtros', {})
        licitaciones_filtradas = []

        for licitacion in licitaciones:
            # Filtro por monto mínimo
            if (filtros.get('monto_minimo', 0) > 
                licitacion.get('monto', 0)):
                continue

            # Filtro por estado
            estados_permitidos = filtros.get('estados', [])
            if (estados_permitidos and 
                licitacion.get('estado') not in estados_permitidos):
                continue

            # Filtro por organismos
            organismos_permitidos = filtros.get('organismos', [])
            if (organismos_permitidos and 
                licitacion.get('organismo') not in organismos_permitidos):
                continue

            licitaciones_filtradas.append(licitacion)

        return licitaciones_filtradas

    def notificar_nuevas_licitaciones(
        self, 
        licitaciones: List[Dict] = None
    ) -> Dict:
        """
        Notificar sobre nuevas licitaciones
        
        Args:
            licitaciones (List[Dict], optional): Lista de licitaciones. 
                                                Si no se proporciona, busca en la base de datos.
        
        Returns:
            Dict: Resumen de notificaciones
        """
        # Si no se proporcionan licitaciones, buscar en la base de datos
        if licitaciones is None:
            # Buscar licitaciones recientes (últimas 24 horas)
            from datetime import datetime, timedelta
            licitaciones = self.persistencia.buscar_licitaciones(
                fecha_desde=datetime.now() - timedelta(days=1)
            )

        # Filtrar licitaciones
        licitaciones_filtradas = self._filtrar_licitaciones(licitaciones)

        # Resumen de notificaciones
        resumen = {
            'total_licitaciones': len(licitaciones),
            'licitaciones_filtradas': len(licitaciones_filtradas),
            'notificaciones_enviadas': {
                'email': 0,
                'telegram': 0,
                'webhook': 0
            }
        }

        # Notificación por email
        if (self.config['email']['habilitado'] and 
            licitaciones_filtradas):
            resumen['notificaciones_enviadas']['email'] = (
                self._notificar_por_email(licitaciones_filtradas)
            )

        # Notificación por Telegram
        if (self.config['telegram']['habilitado'] and 
            licitaciones_filtradas):
            resumen['notificaciones_enviadas']['telegram'] = (
                self._notificar_por_telegram(licitaciones_filtradas)
            )

        # Notificación por Webhook
        if (self.config['webhook']['habilitado'] and 
            licitaciones_filtradas):
            resumen['notificaciones_enviadas']['webhook'] = (
                self._notificar_por_webhook(licitaciones_filtradas)
            )

        return resumen

    def _notificar_por_email(self, licitaciones: List[Dict]) -> int:
        """
        Enviar notificaciones por email
        
        Args:
            licitaciones (List[Dict]): Licitaciones a notificar
        
        Returns:
            int: Número de emails enviados
        """
        config_email = self.config['email']
        
        try:
            # Configuración de email
            msg = MIMEMultipart()
            msg['From'] = config_email['remitente']
            msg['Subject'] = f"Nuevas Licitaciones - {len(licitaciones)} encontradas"

            # Generar cuerpo del email
            cuerpo = "Nuevas Licitaciones:\n\n"
            for licitacion in licitaciones:
                cuerpo += (
                    f"Título: {licitacion.get('titulo', 'N/A')}\n"
                    f"Organismo: {licitacion.get('organismo', 'N/A')}\n"
                    f"Monto: ${licitacion.get('monto', 0):.2f}\n"
                    f"Estado: {licitacion.get('estado', 'N/A')}\n"
                    f"URL: {licitacion.get('url_fuente', 'N/A')}\n\n"
                )

            msg.attach(MIMEText(cuerpo, 'plain'))

            # Conexión SMTP
            with smtplib.SMTP(
                config_email['smtp_host'], 
                config_email['smtp_puerto']
            ) as server:
                server.starttls()
                server.login(
                    config_email['remitente'], 
                    config_email['password']
                )

                # Enviar a cada destinatario
                for destinatario in config_email['destinatarios']:
                    msg['To'] = destinatario
                    server.sendmail(
                        config_email['remitente'], 
                        destinatario, 
                        msg.as_string()
                    )

            return len(config_email['destinatarios'])

        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            return 0

    def _notificar_por_telegram(self, licitaciones: List[Dict]) -> int:
        """
        Enviar notificaciones por Telegram
        
        Args:
            licitaciones (List[Dict]): Licitaciones a notificar
        
        Returns:
            int: Número de mensajes enviados
        """
        config_telegram = self.config['telegram']
        
        try:
            token_bot = config_telegram['token_bot']
            
            # Generar mensaje
            mensaje = f"🏛️ *Nuevas Licitaciones* - {len(licitaciones)} encontradas\n\n"
            for licitacion in licitaciones:
                mensaje += (
                    f"*Título:* {licitacion.get('titulo', 'N/A')}\n"
                    f"*Organismo:* {licitacion.get('organismo', 'N/A')}\n"
                    f"*Monto:* ${licitacion.get('monto', 0):.2f}\n"
                    f"*Estado:* {licitacion.get('estado', 'N/A')}\n"
                    f"*URL:* {licitacion.get('url_fuente', 'N/A')}\n\n"
                )

            # Enviar a cada chat_id
            mensajes_enviados = 0
            for chat_id in config_telegram['chat_ids']:
                response = requests.post(
                    f'https://api.telegram.org/bot{token_bot}/sendMessage',
                    json={
                        'chat_id': chat_id,
                        'text': mensaje,
                        'parse_mode': 'Markdown'
                    }
                )
                
                if response.status_code == 200:
                    mensajes_enviados += 1

            return mensajes_enviados

        except Exception as e:
            self.logger.error(f"Error enviando mensaje de Telegram: {e}")
            return 0

    def _notificar_por_webhook(self, licitaciones: List[Dict]) -> int:
        """
        Enviar notificaciones por Webhook
        
        Args:
            licitaciones (List[Dict]): Licitaciones a notificar
        
        Returns:
            int: Número de webhooks invocados
        """
        config_webhook = self.config['webhook']
        
        try:
            webhooks_invocados = 0
            
            for url_webhook in config_webhook['urls']:
                response = requests.post(
                    url_webhook,
                    json={
                        'evento': 'nuevas_licitaciones',
                        'total': len(licitaciones),
                        'licitaciones': licitaciones
                    }
                )
                
                if response.status_code in [200, 201, 204]:
                    webhooks_invocados += 1

            return webhooks_invocados

        except Exception as e:
            self.logger.error(f"Error invocando webhooks: {e}")
            return 0

# Función de utilidad para crear una instancia
def obtener_notificador(config_path: str = None) -> Notificador:
    """
    Obtener una instancia de Notificador
    
    Args:
        config_path (str, optional): Ruta al archivo de configuración
    
    Returns:
        Notificador: Instancia de notificador
    """
    return Notificador(config_path)
