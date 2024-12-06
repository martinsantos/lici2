from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import logging
import heapq
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(order=True)
class Task:
    priority: TaskPriority
    created_at: datetime
    task_id: str = field(compare=False)
    data: Dict[str, Any] = field(compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    result: Optional[Dict[str, Any]] = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    progress: Optional[Dict[str, Any]] = field(default=None, compare=False)
    batch_id: Optional[str] = field(default=None, compare=False)

    def __post_init__(self):
        self.sort_key = (
            -self.priority.value,  # Negativo para que mayor prioridad sea primero
            self.created_at
        )

class TaskBatch:
    def __init__(self, batch_id: str, max_size: int = 10):
        self.batch_id = batch_id
        self.max_size = max_size
        self.tasks: List[Task] = []
        self.created_at = datetime.now()
        self.status = TaskStatus.PENDING
        self.completed_tasks = 0

    def add_task(self, task: Task) -> bool:
        if len(self.tasks) >= self.max_size:
            return False
        task.batch_id = self.batch_id
        self.tasks.append(task)
        return True

    def is_full(self) -> bool:
        return len(self.tasks) >= self.max_size

    def update_progress(self):
        self.completed_tasks += 1
        if self.completed_tasks == len(self.tasks):
            self.status = TaskStatus.COMPLETED

class TaskQueue:
    def __init__(self, max_concurrent_tasks: int = 3, batch_size: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.batch_size = batch_size
        self.tasks: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.batches: Dict[str, TaskBatch] = {}
        self.current_batch: Optional[TaskBatch] = None
        self._lock = asyncio.Lock()

    async def add_task(self, data: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Añade una nueva tarea a la cola."""
        async with self._lock:
            task = Task(
                task_id=f"task_{len(self.tasks)}_{datetime.now().timestamp()}",
                priority=priority,
                created_at=datetime.now(),
                data=data
            )
            
            # Intentar agregar a batch actual o crear nuevo
            if not self.current_batch or self.current_batch.is_full():
                self.current_batch = TaskBatch(
                    f"batch_{len(self.batches)}_{datetime.now().timestamp()}",
                    self.batch_size
                )
                self.batches[self.current_batch.batch_id] = self.current_batch
            
            self.current_batch.add_task(task)
            heapq.heappush(self.tasks, task)
            
            return task.task_id

    async def get_next_task(self) -> Optional[Task]:
        """Obtiene la siguiente tarea de mayor prioridad."""
        async with self._lock:
            while self.tasks and len(self.running_tasks) < self.max_concurrent_tasks:
                task = heapq.heappop(self.tasks)
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.RUNNING
                    self.running_tasks[task.task_id] = task
                    return task
            return None

    async def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None, 
                          error: Optional[str] = None) -> None:
        """Marca una tarea como completada."""
        async with self._lock:
            if task_id in self.running_tasks:
                task = self.running_tasks.pop(task_id)
                task.status = TaskStatus.COMPLETED if not error else TaskStatus.FAILED
                task.result = result
                task.error = error
                self.completed_tasks[task_id] = task
                
                # Actualizar progreso del batch
                if task.batch_id and task.batch_id in self.batches:
                    self.batches[task.batch_id].update_progress()

    async def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea pendiente o en ejecución."""
        async with self._lock:
            # Buscar en tareas pendientes
            for task in self.tasks:
                if task.task_id == task_id and task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    return True
            
            # Buscar en tareas en ejecución
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                self.running_tasks.pop(task_id)
                self.completed_tasks[task_id] = task
                return True
            
            return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una tarea."""
        for task_dict in [self.running_tasks, self.completed_tasks]:
            if task_id in task_dict:
                task = task_dict[task_id]
                return {
                    "status": task.status.value,
                    "progress": task.progress,
                    "result": task.result,
                    "error": task.error,
                    "batch_id": task.batch_id,
                    "priority": task.priority.name
                }
        
        # Buscar en tareas pendientes
        for task in self.tasks:
            if task.task_id == task_id:
                return {
                    "status": task.status.value,
                    "progress": task.progress,
                    "batch_id": task.batch_id,
                    "priority": task.priority.name
                }
        
        return None

    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de un batch de tareas."""
        if batch_id in self.batches:
            batch = self.batches[batch_id]
            return {
                "batch_id": batch.batch_id,
                "status": batch.status.value,
                "total_tasks": len(batch.tasks),
                "completed_tasks": batch.completed_tasks,
                "created_at": batch.created_at.isoformat()
            }
        return None

    async def update_progress(self, task_id: str, progress: Dict[str, Any]) -> None:
        """Actualiza el progreso de una tarea."""
        async with self._lock:
            if task_id in self.running_tasks:
                self.running_tasks[task_id].progress = progress
            elif task_id in self.completed_tasks:
                self.completed_tasks[task_id].progress = progress
