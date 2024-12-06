from typing import List, Dict, Optional
import aioredis
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, redis_url: str, smtp_config: Dict):
        self.redis = aioredis.from_url(redis_url)
        self.smtp_config = smtp_config
        self.notification_channel = "notifications"

    async def send_notification(self, user_id: str, notification: Dict) -> bool:
        """Envía una notificación a un usuario específico"""
        try:
            notification.update({
                "timestamp": datetime.utcnow().isoformat(),
                "status": "unread"
            })
            
            # Almacenar en Redis
            await self.redis.lpush(
                f"user:{user_id}:notifications",
                json.dumps(notification)
            )
            
            # Publicar en el canal de notificaciones en tiempo real
            await self.redis.publish(
                self.notification_channel,
                json.dumps({
                    "user_id": user_id,
                    "notification": notification
                })
            )

            # Si la notificación requiere email, enviarlo
            if notification.get("send_email", False):
                await self._send_email_notification(
                    user_id,
                    notification["title"],
                    notification["message"]
                )

            return True
        except Exception as e:
            logger.error(f"Error al enviar notificación: {e}")
            return False

    async def get_user_notifications(
        self, user_id: str, 
        start: int = 0, 
        end: int = -1,
        unread_only: bool = False
    ) -> List[Dict]:
        """Obtiene las notificaciones de un usuario"""
        try:
            notifications = await self.redis.lrange(
                f"user:{user_id}:notifications",
                start,
                end
            )
            
            result = []
            for notif in notifications:
                notification = json.loads(notif)
                if unread_only and notification["status"] != "unread":
                    continue
                result.append(notification)
                
            return result
        except Exception as e:
            logger.error(f"Error al obtener notificaciones: {e}")
            return []

    async def mark_as_read(self, user_id: str, notification_ids: List[str]) -> bool:
        """Marca notificaciones como leídas"""
        try:
            notifications = await self.get_user_notifications(user_id)
            updated = False
            
            for i, notif in enumerate(notifications):
                if notif["id"] in notification_ids:
                    notif["status"] = "read"
                    await self.redis.lset(
                        f"user:{user_id}:notifications",
                        i,
                        json.dumps(notif)
                    )
                    updated = True
            
            return updated
        except Exception as e:
            logger.error(f"Error al marcar notificaciones como leídas: {e}")
            return False

    async def _send_email_notification(
        self, user_id: str, 
        subject: str, 
        message: str
    ) -> bool:
        """Envía una notificación por email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["from_email"]
            msg["To"] = await self._get_user_email(user_id)
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            # Enviar email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_config["host"],
                port=self.smtp_config["port"],
                use_tls=True
            ) as smtp:
                await smtp.login(
                    self.smtp_config["username"],
                    self.smtp_config["password"]
                )
                await smtp.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Error al enviar email: {e}")
            return False

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Obtiene el email del usuario desde Redis"""
        try:
            user_data = await self.redis.get(f"user:{user_id}")
            if user_data:
                return json.loads(user_data).get("email")
            return None
        except Exception as e:
            logger.error(f"Error al obtener email del usuario: {e}")
            return None

    async def close(self):
        """Cierra las conexiones"""
        await self.redis.close()
