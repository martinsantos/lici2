from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
import json
from .task_manager import TaskQueue, Task, TaskPriority, TaskProgress, TaskStatus
from .document_analyzer import DocumentAnalyzer
from .scraper import ejecutar_scraper
from .cache_manager import CacheManager, cache_result
from .monitoring import MetricsCollector

logger = logging.getLogger(__name__)

class EnhancedReconCoordinator:
    def __init__(self, max_concurrent_tasks: int = 3, 
                 redis_host: str = 'localhost', 
                 redis_port: int = 6379,
                 metrics_port: int = 9090):
        self.task_queue = TaskQueue(max_concurrent_tasks=max_concurrent_tasks)
        self.cache = CacheManager(host=redis_host, port=redis_port)
        self.metrics = MetricsCollector(metrics_port=metrics_port)
        self.worker_task = None
        self._shutdown = False

    async def start(self):
        """Inicia el coordinador y su worker de procesamiento."""
        if self.worker_task is None:
            self._shutdown = False
            self.worker_task = asyncio.create_task(self._process_tasks())
            logger.info("Coordinador RECON iniciado")

    async def stop(self):
        """Detiene el coordinador de manera ordenada."""
        if self.worker_task:
            self._shutdown = True
            await self.worker_task
            self.worker_task = None
            logger.info("Coordinador RECON detenido")

    async def iniciar_recon(self, plantilla_id: str, plantilla: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Inicia una nueva tarea de reconocimiento con prioridad especificada."""
        task_id = f"recon_{plantilla_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear tarea con la configuración
        task = Task(
            task_id=task_id,
            priority=priority,
            data={
                'plantilla_id': plantilla_id,
                'plantilla': plantilla,
                'total_steps': self._calcular_pasos_totales(plantilla)
            }
        )
        
        # Agregar tarea a la cola
        await self.task_queue.add_task(task)
        logger.info(f"Nueva tarea de reconocimiento creada: {task_id}")
        self.metrics.record_task_start()
        return task_id

    async def iniciar_recon_batch(self, plantillas: List[Dict[str, Any]], 
                                prioridad: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Inicia un nuevo batch de tareas de reconocimiento."""
        batch_tasks = []
        for plantilla in plantillas:
            task_id = await self.task_queue.add_task(
                data={'plantilla': plantilla},
                priority=prioridad
            )
            batch_tasks.append(task_id)
            self.metrics.record_task_start()
        
        # Obtener el batch_id del primer task
        task_status = self.task_queue.get_task_status(batch_tasks[0])
        return task_status['batch_id']

    def _calcular_pasos_totales(self, plantilla: Dict[str, Any]) -> int:
        """Calcula el número total de pasos basado en la plantilla."""
        pasos = 1  # Paso inicial
        if 'configuracion_fuente' in plantilla:
            pasos += 1  # Paso de scraping
        if 'documentos' in plantilla:
            pasos += len(plantilla['documentos'])  # Un paso por documento
        return pasos

    async def _process_tasks(self):
        """Procesa las tareas en la cola de manera continua."""
        while not self._shutdown:
            try:
                # Obtener siguiente tarea
                task = await self.task_queue.get_next_task()
                if not task:
                    await asyncio.sleep(1)  # Esperar si no hay tareas
                    continue

                # Procesar la tarea
                await self._ejecutar_recon(task)

            except Exception as e:
                logger.error(f"Error procesando tareas: {str(e)}")
                await asyncio.sleep(1)

    @cache_result(ttl=3600)  # Cachear resultados por 1 hora
    async def _ejecutar_scraping(self, task: Task, step: int) -> None:
        """Ejecuta el proceso de scraping con caché."""
        try:
            with self.metrics.measure_time():
                await self._update_progress(task, "Ejecutando scraping web", step)
                
                # Intentar obtener resultados del caché
                cache_key = f"scraping:{task.data['plantilla_id']}:{hash(str(task.data['plantilla']))}"
                cached_result = self.cache.get(cache_key)
                
                if cached_result:
                    self.metrics.record_cache_hit()
                    logger.info(f"Usando resultados cacheados para scraping de {task.task_id}")
                    result = cached_result
                else:
                    self.metrics.record_cache_miss()
                    # Ejecutar scraper en un thread separado
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        ejecutar_scraper,
                        task.data['plantilla']
                    )
                    # Cachear resultados
                    self.cache.set(cache_key, result, ttl=3600)
                
                # Almacenar resultados
                if not task.result:
                    task.result = {}
                task.result['scraping'] = result
                
                await self._update_progress(
                    task,
                    "Scraping completado",
                    step,
                    details={"documentos_encontrados": len(result) if result else 0}
                )
                
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error en scraping {task.task_id}: {str(e)}")
            raise

    async def _ejecutar_recon(self, task: Task) -> None:
        """Ejecuta una tarea de reconocimiento."""
        try:
            with self.metrics.measure_time():
                plantilla = task.data['plantilla']
                current_step = 1
                
                # Actualizar progreso inicial
                await self._update_progress(task, "Iniciando reconocimiento", current_step)
                
                # Fase 1: Scraping web
                if 'configuracion_fuente' in plantilla:
                    await self._ejecutar_scraping(task, current_step)
                    current_step += 1
                
                # Fase 2: Análisis de documentos
                if 'documentos' in plantilla:
                    await self._analizar_documentos(task, current_step)
                
                # Almacenar resultados en caché
                self.cache.set_task_result(task.task_id, task.result)
                
                # Marcar como completado
                await self.task_queue.complete_task(task.task_id, result=task.result)
                self.metrics.record_task_complete()
                
        except Exception as e:
            self.metrics.record_error()
            error_msg = f"Error en tarea {task.task_id}: {str(e)}"
            logger.error(error_msg)
            await self.task_queue.complete_task(task.task_id, error=error_msg)

    async def _analizar_documentos(self, task: Task, start_step: int) -> None:
        """Analiza los documentos especificados en la plantilla."""
        try:
            analyzer = DocumentAnalyzer(task.data['plantilla'])
            resultados = []
            current_step = start_step
            
            for doc in task.data['plantilla']['documentos']:
                await self._update_progress(
                    task,
                    f"Analizando documento: {doc['ruta']}",
                    current_step
                )
                
                try:
                    resultado = analyzer.analizar_documento(doc['ruta'])
                    resultados.append({
                        'documento': doc['ruta'],
                        'resultado': resultado
                    })
                    
                    await self._update_progress(
                        task,
                        f"Documento analizado: {doc['ruta']}",
                        current_step,
                        details={"campos_extraidos": len(resultado) if resultado else 0}
                    )
                    
                except Exception as e:
                    logger.error(f"Error analizando documento {doc['ruta']}: {str(e)}")
                    resultados.append({
                        'documento': doc['ruta'],
                        'error': str(e)
                    })
                
                current_step += 1
            
            if not task.result:
                task.result = {}
            task.result['analisis'] = resultados
            
        except Exception as e:
            logger.error(f"Error en análisis de documentos {task.task_id}: {str(e)}")
            raise

    async def _update_progress(self, task: Task, step_description: str, current_step: int, details: Optional[Dict[str, Any]] = None) -> None:
        """Actualiza el progreso de una tarea."""
        total_steps = task.data['total_steps']
        percentage = (current_step / total_steps) * 100 if total_steps > 0 else 0
        
        progress = TaskProgress(
            current_step=step_description,
            total_steps=total_steps,
            current_step_number=current_step,
            details=details,
            percentage=percentage
        )
        
        await self.task_queue.update_progress(task.task_id, progress)

    def obtener_estado(self, task_id: str) -> Dict[str, Any]:
        """Obtiene el estado actual de una tarea."""
        # Intentar obtener de la cola activa
        estado = self.task_queue.get_task_status(task_id)
        if not estado:
            # Si no está en la cola, buscar en caché
            cached_result = self.cache.get_task_result(task_id)
            if cached_result:
                return {
                    'estado': 'completado',
                    'resultados': cached_result,
                    'desde_cache': True
                }
            return {'estado': 'no_encontrado'}
        return estado

    def obtener_estado_batch(self, batch_id: str) -> Dict[str, Any]:
        """Obtiene el estado de un batch de tareas."""
        batch_status = self.task_queue.get_batch_status(batch_id)
        if not batch_status:
            raise ValueError(f"Batch {batch_id} no encontrado")
        return batch_status

    async def cancelar_tarea(self, task_id: str) -> bool:
        """Cancela una tarea en curso."""
        return await self.task_queue.cancel_task(task_id)

    async def limpiar_cache(self, max_age_hours: int = 24) -> None:
        """Esta funcionalidad ahora es manejada automáticamente por el TaskQueue."""
        pass  # La limpieza se maneja en el TaskQueue

    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtiene las métricas actuales del sistema."""
        return json.loads(self.metrics.to_json())
