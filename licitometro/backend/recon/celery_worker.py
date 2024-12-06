import os
from dotenv import load_dotenv
from celery import Celery
import logging

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de Celery
def create_celery_app():
    """
    Crea y configura la aplicación Celery
    """
    app = Celery(
        'recon_tasks',
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )

    # Importar tareas
    app.autodiscover_tasks(['backend.recon'], force=True)

    # Configuraciones adicionales
    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
        worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
    )

    return app

# Crear instancia de Celery
celery_app = create_celery_app()

def start_worker(concurrency=4, queues=None):
    """
    Inicia un worker de Celery con configuraciones personalizadas
    
    :param concurrency: Número de workers concurrentes
    :param queues: Colas específicas a procesar
    """
    from celery.bin import worker

    worker_instance = worker.worker(app=celery_app)
    
    options = {
        'concurrency': concurrency,
        'loglevel': 'INFO',
        'traceback': True
    }

    if queues:
        options['queues'] = queues

    worker_instance.run(**options)

def start_beat():
    """
    Inicia el servicio de tareas programadas (beat)
    """
    from celery.bin import beat

    beat_instance = beat.beat(app=celery_app)
    beat_instance.run()

def start_flower(port=5555):
    """
    Inicia el servicio de monitoreo Flower
    
    :param port: Puerto para el dashboard de Flower
    """
    from flower.command import FlowerCommand

    flower_command = FlowerCommand(celery_app)
    flower_command.execute_from_commandline([
        'flower',
        f'--port={port}',
        '--broker=' + celery_app.conf.broker_url
    ])

# Punto de entrada principal
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'worker':
            # Ejemplo: python celery_worker.py worker
            start_worker()
        elif command == 'beat':
            # Ejemplo: python celery_worker.py beat
            start_beat()
        elif command == 'flower':
            # Ejemplo: python celery_worker.py flower
            start_flower()
        else:
            print("Comando no reconocido. Usa 'worker', 'beat' o 'flower'.")
    else:
        print("Por favor especifica un comando: worker, beat o flower.")
