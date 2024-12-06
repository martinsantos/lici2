from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

from .coordinator import ReconCoordinator

router = APIRouter(prefix="/recon", tags=["recon"])
coordinator = ReconCoordinator()

class PlantillaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fuente: str
    configuracion_fuente: Optional[Dict[str, Any]] = None
    documentos: Optional[list] = None
    reglas: Dict[str, Any]
    mapeo: Dict[str, Any]

class EstadoTarea(BaseModel):
    task_id: str
    estado: str
    inicio: Optional[str] = None
    fin: Optional[str] = None
    error: Optional[str] = None
    resultados: Optional[list] = None

@router.post("/iniciar", response_model=Dict[str, str])
async def iniciar_recon(plantilla: PlantillaBase):
    """Inicia una nueva tarea de reconocimiento basada en una plantilla."""
    try:
        task_id = await coordinator.iniciar_recon(
            plantilla_id=plantilla.nombre,
            plantilla=plantilla.dict()
        )
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estado/{task_id}", response_model=EstadoTarea)
def obtener_estado(task_id: str):
    """Obtiene el estado actual de una tarea de reconocimiento."""
    estado = coordinator.obtener_estado(task_id)
    if estado['estado'] == 'no_encontrado':
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return EstadoTarea(task_id=task_id, **estado)

@router.delete("/cancelar/{task_id}")
def cancelar_tarea(task_id: str):
    """Cancela una tarea de reconocimiento en curso."""
    if coordinator.cancelar_tarea(task_id):
        return {"mensaje": "Tarea cancelada exitosamente"}
    raise HTTPException(status_code=404, detail="Tarea no encontrada o ya finalizada")

@router.post("/limpiar-cache")
def limpiar_cache(background_tasks: BackgroundTasks, max_age_hours: int = 24):
    """Limpia resultados antiguos del cache."""
    background_tasks.add_task(coordinator.limpiar_cache, max_age_hours)
    return {"mensaje": "Limpieza de cache iniciada"}

# Ejemplo de plantilla para documentación
ejemplo_plantilla = {
    "nombre": "ejemplo_licitacion",
    "descripcion": "Plantilla de ejemplo para extracción de licitaciones",
    "fuente": "https://ejemplo.com/licitaciones",
    "configuracion_fuente": {
        "url_inicial": "https://ejemplo.com/licitaciones",
        "tipo": "web"
    },
    "reglas": {
        "selectores_lista": ["div.licitacion-item"],
        "selector_siguiente": "a.siguiente-pagina::attr(href)",
        "validaciones": {
            "monto": {
                "tipo": "numero",
                "rango": [0, 1000000000]
            }
        }
    },
    "mapeo": {
        "titulo": {
            "tipo": "css",
            "selector": "h2.titulo::text",
            "transformaciones": [{"tipo": "texto"}]
        },
        "monto": {
            "tipo": "css",
            "selector": "span.monto::text",
            "transformaciones": [{"tipo": "numero"}]
        },
        "fecha_publicacion": {
            "tipo": "css",
            "selector": "span.fecha::text",
            "transformaciones": [
                {
                    "tipo": "fecha",
                    "formato": "%Y-%m-%d"
                }
            ]
        }
    }
}
