from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
import logging

from .enhanced_coordinator import EnhancedReconCoordinator, TaskPriority

logger = logging.getLogger(__name__)

class PrioridadTarea(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

class PlantillaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fuente: str
    prioridad: PrioridadTarea = Field(default=PrioridadTarea.MEDIA)
    configuracion_fuente: Optional[Dict[str, Any]] = None
    documentos: Optional[list] = None
    reglas: Dict[str, Any]
    mapeo: Dict[str, Any]

class EstadoTarea(BaseModel):
    task_id: str
    estado: str
    prioridad: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    resultados: Optional[Dict[str, Any]] = None

router = APIRouter(prefix="/recon", tags=["recon"])
coordinator = None

@router.on_event("startup")
async def startup_event():
    global coordinator
    coordinator = EnhancedReconCoordinator(
        max_concurrent_tasks=3,
        redis_host='localhost',
        redis_port=6379,
        metrics_port=9090
    )
    await coordinator.start()
    logger.info("Módulo RECON iniciado")

@router.on_event("shutdown")
async def shutdown_event():
    if coordinator:
        await coordinator.shutdown()
    logger.info("Módulo RECON detenido")

@router.post("/iniciar", response_model=Dict[str, str])
async def iniciar_recon(plantilla: PlantillaBase):
    """Inicia una nueva tarea de reconocimiento basada en una plantilla."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    try:
        # Convertir prioridad de enum a TaskPriority
        prioridad_map = {
            PrioridadTarea.BAJA: TaskPriority.LOW,
            PrioridadTarea.MEDIA: TaskPriority.MEDIUM,
            PrioridadTarea.ALTA: TaskPriority.HIGH,
            PrioridadTarea.CRITICA: TaskPriority.CRITICAL
        }
        
        task_id = await coordinator.iniciar_recon(
            plantilla_id=plantilla.nombre,
            plantilla=plantilla.dict(exclude={'prioridad'}),
            priority=prioridad_map[plantilla.prioridad]
        )
        return {"task_id": task_id}
    except Exception as e:
        logger.error(f"Error al iniciar reconocimiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estado/{task_id}", response_model=EstadoTarea)
def obtener_estado(task_id: str):
    """Obtiene el estado actual de una tarea de reconocimiento."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    estado = coordinator.obtener_estado(task_id)
    if not estado:
        raise HTTPException(status_code=404, detail="Task not found")
    return EstadoTarea(task_id=task_id, **estado)

@router.delete("/cancelar/{task_id}")
async def cancelar_tarea(task_id: str):
    """Cancela una tarea de reconocimiento en curso."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    success = await coordinator.cancelar_tarea(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    return {"status": "cancelled"}

@router.get("/metrics")
async def get_metrics():
    """Obtiene las métricas actuales del sistema."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    return coordinator.obtener_metricas()

@router.get("/health")
async def health_check():
    """Endpoint para verificar la salud del servicio."""
    if not coordinator:
        raise HTTPException(status_code=503, detail="Coordinator not initialized")
    
    metrics = coordinator.obtener_metricas()
    health_status = {
        "status": "healthy",
        "cpu_usage": metrics["cpu_usage"],
        "memory_usage": metrics["memory_usage"],
        "active_tasks": metrics["active_tasks"],
        "error_count": metrics["error_count"]
    }
    
    # Considerar no saludable si hay demasiados errores o uso excesivo de recursos
    if (metrics["error_count"] > 100 or 
        metrics["cpu_usage"] > 90 or 
        metrics["memory_usage"] > 90):
        health_status["status"] = "unhealthy"
        
    return health_status

@router.post("/batch/recon")
async def iniciar_recon_batch(plantillas: List[Dict[str, Any]], 
                            prioridad: Optional[str] = None):
    """Inicia un batch de tareas de reconocimiento."""
    try:
        task_priority = TaskPriority[prioridad.upper()] if prioridad else TaskPriority.MEDIUM
        batch_id = await coordinator.iniciar_recon_batch(plantillas, task_priority)
        return {"batch_id": batch_id, "mensaje": "Batch de reconocimiento iniciado"}
    except Exception as e:
        logger.error(f"Error al iniciar batch de reconocimiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{batch_id}")
async def obtener_estado_batch(batch_id: str):
    """Obtiene el estado de un batch de tareas."""
    try:
        estado = coordinator.obtener_estado_batch(batch_id)
        return estado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener estado del batch {batch_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Ejemplo de plantilla para documentación
ejemplo_plantilla = {
    "nombre": "ejemplo_licitacion",
    "descripcion": "Plantilla de ejemplo para extracción de licitaciones",
    "fuente": "web",
    "prioridad": "MEDIA",
    "configuracion_fuente": {
        "url": "https://ejemplo.com/licitaciones",
        "tipo": "web",
        "parametros": {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }
    },
    "documentos": [
        {
            "ruta": "/ruta/al/documento1.pdf",
            "tipo": "bases"
        },
        {
            "ruta": "/ruta/al/documento2.xlsx",
            "tipo": "anexo_tecnico"
        }
    ],
    "reglas": {
        "extraccion": {
            "numero_licitacion": {
                "patron": r"Licitación N°\s*(\d+[-/]\d+)",
                "obligatorio": True
            },
            "monto": {
                "patron": r"\$\s*([\d,]+(?:\.\d{2})?)",
                "tipo": "numero"
            }
        },
        "validaciones": {
            "monto": {
                "tipo": "numero",
                "rango": [0, 1000000000]
            }
        }
    },
    "mapeo": {
        "campos_salida": {
            "numero_licitacion": "id",
            "monto": "valor_total"
        }
    }
}
