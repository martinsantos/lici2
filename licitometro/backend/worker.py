from celery import Celery
from config import settings

celery_app = Celery(
    'licitometro',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['licitaciones.tasks']
)

# Optional configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Argentina/Mendoza',
    enable_utc=True,
    task_track_started=True,
    task_publish_retry=True,
    task_publish_retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    }
)
