from fastapi import FastAPI, HTTPException
from redis import Redis
from typing import Dict, Any, List, Optional
import json
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_username: str = None,
        smtp_password: str = None
    ):
        self.app = FastAPI()
        self.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.smtp_config = {
            "hostname": smtp_host,
            "port": smtp_port,
            "username": smtp_username,
            "password": smtp_password,
            "use_tls": True
        }
        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/notify/user/{user_id}")
        async def notify_user(
            user_id: str,
            notification: Dict[str, Any]
        ):
            try:
                notification_id = await self.save_notification(user_id, notification)
                if "email" in notification and self.smtp_config["username"]:
                    await self.send_email_notification(
                        to_email=notification["email"],
                        subject=notification.get("subject", "Nueva notificación"),
                        body=notification.get("body", "")
                    )
                return {
                    "status": "success",
                    "notification_id": notification_id
                }
            except Exception as e:
                logger.error(f"Error sending notification: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/notifications/{user_id}")
        async def get_user_notifications(
            user_id: str,
            unread_only: bool = False
        ) -> List[Dict[str, Any]]:
            try:
                return await self.get_notifications(user_id, unread_only)
            except Exception as e:
                logger.error(f"Error retrieving notifications: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/notifications/{user_id}/{notification_id}/mark-read")
        async def mark_notification_read(
            user_id: str,
            notification_id: str
        ):
            try:
                await self.mark_as_read(user_id, notification_id)
                return {"status": "success"}
            except Exception as e:
                logger.error(f"Error marking notification as read: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    async def save_notification(
        self,
        user_id: str,
        notification: Dict[str, Any]
    ) -> str:
        try:
            notification_id = f"notification:{user_id}:{self.redis.incr('notification_counter')}"
            notification.update({
                "id": notification_id,
                "read": False,
                "timestamp": self.redis.time()[0]
            })
            self.redis.hset(
                f"user:{user_id}:notifications",
                notification_id,
                json.dumps(notification)
            )
            return notification_id
        except Exception as e:
            logger.error(f"Error saving notification: {str(e)}")
            raise

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        try:
            notifications = []
            all_notifications = self.redis.hgetall(f"user:{user_id}:notifications")
            for notification_json in all_notifications.values():
                notification = json.loads(notification_json)
                if not unread_only or not notification["read"]:
                    notifications.append(notification)
            notifications.sort(key=lambda x: x["timestamp"], reverse=True)
            return notifications
        except Exception as e:
            logger.error(f"Error retrieving notifications: {str(e)}")
            raise

    async def mark_as_read(self, user_id: str, notification_id: str):
        try:
            notification_key = f"user:{user_id}:notifications"
            notification_json = self.redis.hget(notification_key, notification_id)
            if notification_json:
                notification = json.loads(notification_json)
                notification["read"] = True
                self.redis.hset(
                    notification_key,
                    notification_id,
                    json.dumps(notification)
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Notification {notification_id} not found"
                )
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise

    async def send_email_notification(
        self,
        to_email: str,
        subject: str,
        body: str
    ):
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_config["username"]
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            await aiosmtplib.send(
                message,
                hostname=self.smtp_config["hostname"],
                port=self.smtp_config["port"],
                username=self.smtp_config["username"],
                password=self.smtp_config["password"],
                use_tls=self.smtp_config["use_tls"]
            )
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
