import asyncio
from typing import Any, Callable, Dict, List, Optional
import logging
import time
from datetime import datetime
import json
from functools import wraps
import ioredis
from fastapi import BackgroundTasks
from prom_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Métricas de Prometheus para tareas en segundo plano
TASK_COUNT = Counter(
    'background_task_total',
    'Total de tareas en segundo plano',
    ['task_type', 'status']
)

TASK_DURATION = Histogram(
    'background_task_duration_seconds',
    'Duración de tareas en segundo plano',
    ['task_type']
)

class BackgroundTaskManager:
    def __init__(
        self,
        redis_url: str,
        max_retries: int = 3,
        retry_delay: int = 60,
        task_timeout: int = 3600
    ):
        self.redis = ioredis.from_url(redis_url)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.task_timeout = task_timeout
        self._tasks: Dict[str, asyncio.Task] = {}

    async def add_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        **kwargs
    ) -> str:
        """
        Agrega una nueva tarea en segundo plano
        
        Args:
            task_id: Identificador único de la tarea
            func: Función a ejecutar
            *args, **kwargs: Argumentos para la función
        """
        task_info = {
            'id': task_id,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'retries': 0,
            'args': args,
            'kwargs': kwargs,
            'last_error': None
        }

        # Guardar información de la tarea en Redis
        await self.redis.set(
            f"task:{task_id}",
            json.dumps(task_info),
            'EX',
            self.task_timeout
        )

        # Crear y programar la tarea
        task = asyncio.create_task(
            self._execute_task(task_id, func, *args, **kwargs)
        )
        self._tasks[task_id] = task

        TASK_COUNT.labels(
            task_type=func.__name__,
            status='created'
        ).inc()

        return task_id

    async def _execute_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        **kwargs
    ):
        """Ejecuta una tarea con manejo de errores y reintentos"""
        start_time = time.time()
        task_info = json.loads(
            await self.redis.get(f"task:{task_id}")
        )

        try:
            # Actualizar estado a 'running'
            task_info['status'] = 'running'
            task_info['started_at'] = datetime.utcnow().isoformat()
            await self.redis.set(
                f"task:{task_id}",
                json.dumps(task_info),
                'EX',
                self.task_timeout
            )

            # Ejecutar la función
            result = await func(*args, **kwargs)

            # Actualizar estado a 'completed'
            task_info['status'] = 'completed'
            task_info['completed_at'] = datetime.utcnow().isoformat()
            task_info['result'] = result
            await self.redis.set(
                f"task:{task_id}",
                json.dumps(task_info),
                'EX',
                self.task_timeout
            )

            TASK_COUNT.labels(
                task_type=func.__name__,
                status='completed'
            ).inc()

        except Exception as e:
            logger.error(f"Error en tarea {task_id}: {str(e)}")
            task_info['last_error'] = str(e)
            task_info['retries'] += 1

            if task_info['retries'] < self.max_retries:
                # Programar reintento
                task_info['status'] = 'pending'
                await self.redis.set(
                    f"task:{task_id}",
                    json.dumps(task_info),
                    'EX',
                    self.task_timeout
                )
                
                await asyncio.sleep(self.retry_delay)
                await self._execute_task(task_id, func, *args, **kwargs)
            else:
                # Marcar como fallida
                task_info['status'] = 'failed'
                await self.redis.set(
                    f"task:{task_id}",
                    json.dumps(task_info),
                    'EX',
                    self.task_timeout
                )

                TASK_COUNT.labels(
                    task_type=func.__name__,
                    status='failed'
                ).inc()

        finally:
            duration = time.time() - start_time
            TASK_DURATION.labels(
                task_type=func.__name__
            ).observe(duration)

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una tarea"""
        task_info = await self.redis.get(f"task:{task_id}")
        return json.loads(task_info) if task_info else None

    async def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea en ejecución"""
        task = self._tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            
            # Actualizar estado en Redis
            task_info = json.loads(
                await self.redis.get(f"task:{task_id}")
            )
            task_info['status'] = 'cancelled'
            await self.redis.set(
                f"task:{task_id}",
                json.dumps(task_info),
                'EX',
                self.task_timeout
            )
            
            return True
        return False

    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Limpia tareas antiguas de Redis"""
        cursor = '0'
        while cursor != 0:
            cursor, keys = await self.redis.scan(
                cursor,
                match="task:*",
                count=100
            )
            
            for key in keys:
                task_info = json.loads(await self.redis.get(key))
                created_at = datetime.fromisoformat(task_info['created_at'])
                age_hours = (
                    datetime.utcnow() - created_at
                ).total_seconds() / 3600

                if age_hours > max_age_hours:
                    await self.redis.delete(key)

    def background_task(
        self,
        task_type: str,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ) -> Callable:
        """
        Decorador para marcar una función como tarea en segundo plano
        
        Args:
            task_type: Tipo de tarea para identificación
            max_retries: Número máximo de reintentos (opcional)
            retry_delay: Tiempo entre reintentos en segundos (opcional)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                task_id = f"{task_type}_{int(time.time() * 1000)}"
                return await self.add_task(
                    task_id,
                    func,
                    *args,
                    **kwargs
                )
            return wrapper
        return decorator

    async def close(self):
        """Cierra las conexiones y limpia los recursos"""
        # Cancelar todas las tareas activas
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
        
        # Esperar a que todas las tareas se cancelen
        if self._tasks:
            await asyncio.gather(
                *self._tasks.values(),
                return_exceptions=True
            )
        
        # Cerrar conexión Redis
        await self.redis.quit()
