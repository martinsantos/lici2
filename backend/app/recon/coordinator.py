from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from .scraper import ejecutar_scraper
from .document_analyzer import DocumentAnalyzer

logger = logging.getLogger(__name__)

class ReconCoordinator:
    def __init__(self):
        self.active_tasks = {}
        self.results_cache = {}
    
    async def iniciar_recon(self, plantilla_id: str, plantilla: Dict[str, Any]) -> str:
        """Inicia una nueva tarea de reconocimiento basada en una plantilla."""
        task_id = f"recon_{plantilla_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear tarea asíncrona
        task = asyncio.create_task(
            self._ejecutar_recon(task_id, plantilla)
        )
        
        self.active_tasks[task_id] = {
            'task': task,
            'estado': 'iniciado',
            'inicio': datetime.now().isoformat(),
            'plantilla_id': plantilla_id
        }
        
        return task_id
    
    async def _ejecutar_recon(self, task_id: str, plantilla: Dict[str, Any]) -> None:
        """Ejecuta el proceso de reconocimiento completo."""
        try:
            self.active_tasks[task_id]['estado'] = 'en_progreso'
            
            # Fase 1: Scraping web
            if 'configuracion_fuente' in plantilla:
                await self._ejecutar_scraping(task_id, plantilla)
            
            # Fase 2: Análisis de documentos
            if 'documentos' in plantilla:
                await self._analizar_documentos(task_id, plantilla)
            
            # Marcar como completado
            self.active_tasks[task_id]['estado'] = 'completado'
            self.active_tasks[task_id]['fin'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error en tarea {task_id}: {str(e)}")
            self.active_tasks[task_id]['estado'] = 'error'
            self.active_tasks[task_id]['error'] = str(e)
    
    async def _ejecutar_scraping(self, task_id: str, plantilla: Dict[str, Any]) -> None:
        """Ejecuta el proceso de scraping."""
        try:
            # Ejecutar scraper en un thread separado para no bloquear
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                ejecutar_scraper,
                plantilla
            )
        except Exception as e:
            logger.error(f"Error en scraping {task_id}: {str(e)}")
            raise
    
    async def _analizar_documentos(self, task_id: str, plantilla: Dict[str, Any]) -> None:
        """Analiza los documentos especificados en la plantilla."""
        try:
            analyzer = DocumentAnalyzer(plantilla)
            resultados = []
            
            for doc in plantilla['documentos']:
                resultado = analyzer.analizar_documento(doc['ruta'])
                resultados.append({
                    'documento': doc['ruta'],
                    'resultado': resultado
                })
            
            self.results_cache[task_id] = resultados
            
        except Exception as e:
            logger.error(f"Error en análisis de documentos {task_id}: {str(e)}")
            raise
    
    def obtener_estado(self, task_id: str) -> Dict[str, Any]:
        """Obtiene el estado actual de una tarea de reconocimiento."""
        if task_id not in self.active_tasks:
            return {'estado': 'no_encontrado'}
        
        estado = self.active_tasks[task_id].copy()
        
        # Agregar resultados si están disponibles
        if task_id in self.results_cache:
            estado['resultados'] = self.results_cache[task_id]
        
        return estado
    
    def cancelar_tarea(self, task_id: str) -> bool:
        """Cancela una tarea de reconocimiento en curso."""
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]['task']
        if not task.done():
            task.cancel()
            self.active_tasks[task_id]['estado'] = 'cancelado'
            return True
        
        return False
    
    def limpiar_cache(self, max_age_hours: int = 24) -> None:
        """Limpia resultados antiguos del cache."""
        tiempo_limite = datetime.now().timestamp() - (max_age_hours * 3600)
        
        # Limpiar tareas antiguas
        tareas_a_eliminar = []
        for task_id, task_info in self.active_tasks.items():
            if 'fin' in task_info:
                tiempo_fin = datetime.fromisoformat(task_info['fin']).timestamp()
                if tiempo_fin < tiempo_limite:
                    tareas_a_eliminar.append(task_id)
        
        # Eliminar tareas y resultados antiguos
        for task_id in tareas_a_eliminar:
            del self.active_tasks[task_id]
            if task_id in self.results_cache:
                del self.results_cache[task_id]
