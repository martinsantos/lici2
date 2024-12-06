import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .performance import CircuitBreaker, RateLimiter
from .cache_manager import CacheManager
from .background_tasks import BackgroundTaskManager
from .mendoza_client import MendozaClient  # Importar el cliente de Mendoza
from ..services.notifications.notification_service import NotificationService

logger = logging.getLogger(__name__)

class ReconCoordinator:
    def __init__(
        self,
        cache_manager: CacheManager,
        task_manager: BackgroundTaskManager
    ):
        self.cache = cache_manager
        self.task_manager = task_manager
        self.notification_service = NotificationService()
        
        # Circuit breakers para cada servicio
        self.circuit_breakers = {
            'comprar': CircuitBreaker('comprar'),
            'contratar': CircuitBreaker('contratar'),
            'bac': CircuitBreaker('bac'),
            'comprar_mendoza': CircuitBreaker('comprar_mendoza'),
            'compras_mendoza': CircuitBreaker('compras_mendoza')
        }
        
        # Rate limiters para cada servicio
        self.rate_limiters = {
            'comprar': RateLimiter(rate=100, period=60),    # 100 req/min
            'contratar': RateLimiter(rate=120, period=60),  # 120 req/min
            'bac': RateLimiter(rate=80, period=60),         # 80 req/min
            'comprar_mendoza': RateLimiter(rate=60, period=60),  # 60 req/min
            'compras_mendoza': RateLimiter(rate=60, period=60)   # 60 req/min
        }
        
        # Semáforo para control de concurrencia global
        self.semaphore = asyncio.Semaphore(10)  # Máximo 10 tareas concurrentes
        
        # Estado de las tareas
        self.tasks: Dict[str, dict] = {}

    async def iniciar_recon(
        self,
        query: str,
        sources: List[str] = None,
        max_results: int = 100,
        filtros: Optional[Dict] = None
    ) -> str:
        """
        Inicia una tarea de reconocimiento
        
        Args:
            query: Consulta de búsqueda
            sources: Lista de fuentes a consultar (opcional)
            max_results: Número máximo de resultados por fuente
            filtros: Filtros adicionales (fechas, categorías, etc.)
            
        Returns:
            str: ID de la tarea
        """
        task_id = str(uuid4())
        
        # Configurar fuentes por defecto si no se especifican
        if not sources:
            sources = ['comprar', 'contratar', 'bac', 'comprar_mendoza', 'compras_mendoza']
            
        # Inicializar estado de la tarea
        self.tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'sources': sources,
            'results': {},
            'errors': [],
            'start_time': datetime.utcnow(),
            'query': query,
            'filtros': filtros or {}
        }
        
        # Iniciar tarea en background
        self.task_manager.create_task(
            self._ejecutar_recon(task_id, query, sources, max_results, filtros)
        )
        
        return task_id

    async def _ejecutar_recon(
        self,
        task_id: str,
        query: str,
        sources: List[str],
        max_results: int,
        filtros: Optional[Dict] = None
    ):
        """Ejecuta la tarea de reconocimiento"""
        try:
            tasks = []
            for source in sources:
                task = self._buscar_en_fuente(
                    task_id, source, query, max_results, filtros
                )
                tasks.append(task)
            
            # Ejecutar búsquedas en paralelo
            await asyncio.gather(*tasks)
            
            # Actualizar estado final
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['progress'] = 100
            
        except Exception as e:
            logger.error(f"Error en tarea {task_id}: {str(e)}")
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['errors'].append(str(e))

    async def _buscar_en_fuente(
        self,
        task_id: str,
        source: str,
        query: str,
        max_results: int,
        filtros: Optional[Dict] = None
    ):
        """Busca en una fuente específica"""
        try:
            async with self.semaphore:
                async with self.circuit_breakers[source]:
                    async with self.rate_limiters[source].limit():
                        # Buscar en caché primero
                        cache_key = f"{source}:{query}:{hash(str(filtros))}"
                        cached_results = await self.cache.get(cache_key)
                        
                        if cached_results:
                            self.tasks[task_id]['results'][source] = cached_results
                            return
                        
                        # Si no está en caché, hacer la búsqueda
                        if source in ['comprar_mendoza', 'compras_mendoza']:
                            results = await self._search_mendoza(query, filtros)
                        else:
                            results = await self._realizar_busqueda(
                                source, query, max_results, filtros
                            )
                        
                        # Guardar en caché
                        await self.cache.set(
                            cache_key,
                            results,
                            expire=3600  # 1 hora
                        )
                        
                        # Actualizar resultados y progreso
                        self.tasks[task_id]['results'][source] = results
                        self._actualizar_progreso(task_id, source)
                        
                        # Notificar nuevas licitaciones
                        for tender_data in results:
                            is_new_tender = True  # TO DO: implementar lógica para determinar si es una nueva licitación
                            if is_new_tender:
                                await self.notification_service.notify_user(
                                    user_id="admin",
                                    notification={
                                        "type": "new_tender",
                                        "subject": f"Nueva licitación: {tender_data['title']}",
                                        "body": f"Se ha detectado una nueva licitación: {tender_data['title']}\nOrganismo: {tender_data['organization']}\nFecha límite: {tender_data['deadline']}",
                                        "tender_id": tender_data["id"],
                                        "email": "admin@example.com"  # Configurar email real
                                    }
                                )
                        
        except Exception as e:
            logger.error(f"Error buscando en {source}: {str(e)}")
            self.tasks[task_id]['errors'].append(
                f"Error en {source}: {str(e)}"
            )

    def _actualizar_progreso(self, task_id: str, source: str):
        """Actualiza el progreso de la tarea"""
        task = self.tasks[task_id]
        completed = len([s for s in task['sources'] if s in task['results']])
        task['progress'] = int((completed / len(task['sources'])) * 100)

    async def _realizar_busqueda(
        self,
        source: str,
        query: str,
        max_results: int,
        filtros: Optional[Dict] = None
    ) -> List[dict]:
        """
        Realiza la búsqueda en una fuente específica
        
        Esta es una implementación base que debe ser sobrescrita
        por las clases específicas de cada fuente
        """
        raise NotImplementedError(
            "Debe implementar _realizar_busqueda en una subclase"
        )

    async def _search_mendoza(self, query: str, filters: Dict = None) -> List[Dict]:
        """Busca licitaciones en los portales de Mendoza"""
        results = []
        
        async with MendozaClient() as client:
            try:
                # Buscar en Comprar Mendoza
                if self._check_circuit('comprar_mendoza'):
                    async with self.rate_limiters['comprar_mendoza']:
                        comprar_results = await client.buscar_comprar_mendoza(
                            query=query,
                            filtros=filters
                        )
                        results.extend([
                            {**r, 'source': 'comprar_mendoza'}
                            for r in comprar_results
                        ])
                
                # Buscar en Compras Mendoza
                if self._check_circuit('compras_mendoza'):
                    async with self.rate_limiters['compras_mendoza']:
                        compras_results = await client.buscar_compras_mendoza(
                            query=query,
                            filtros=filters
                        )
                        results.extend([
                            {**r, 'source': 'compras_mendoza'}
                            for r in compras_results
                        ])
                        
            except Exception as e:
                logger.error(f"Error buscando en Mendoza: {str(e)}")
                self._trip_circuit('comprar_mendoza')
                self._trip_circuit('compras_mendoza')
        
        return results

    async def _get_details_mendoza(self, source: str, item_id: str) -> Dict:
        """Obtiene detalles de una licitación de Mendoza"""
        async with MendozaClient() as client:
            try:
                if source == 'comprar_mendoza':
                    if self._check_circuit('comprar_mendoza'):
                        async with self.rate_limiters['comprar_mendoza']:
                            return await client.obtener_detalle_comprar(item_id)
                            
                elif source == 'compras_mendoza':
                    if self._check_circuit('compras_mendoza'):
                        async with self.rate_limiters['compras_mendoza']:
                            return await client.obtener_detalle_compras(item_id)
                            
            except Exception as e:
                logger.error(f"Error obteniendo detalles de Mendoza: {str(e)}")
                self._trip_circuit(source)
                raise

    async def obtener_estado_tarea(self, task_id: str) -> Optional[dict]:
        """Obtiene el estado actual de una tarea"""
        return self.tasks.get(task_id)

    async def cancelar_tarea(self, task_id: str) -> bool:
        """Cancela una tarea en progreso"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'cancelled'
            return True
        return False

    async def get_details(self, source: str, item_id: str) -> Dict:
        """Obtiene los detalles de una licitación específica"""
        if source == 'comprar':
            return await self._get_details_comprar(item_id)
        elif source == 'contratar':
            return await self._get_details_contratar(item_id)
        elif source == 'bac':
            return await self._get_details_bac(item_id)
        elif source in ['comprar_mendoza', 'compras_mendoza']:
            return await self._get_details_mendoza(source, item_id)
        else:
            raise ValueError(f"Fuente no soportada: {source}")

    async def _search_all(self, query: str, sources: List[str], filters: Dict = None) -> List[Dict]:
        """Busca en todas las fuentes habilitadas"""
        tasks = []
        
        for source in sources:
            if source == 'comprar':
                tasks.append(self._search_comprar(query, filters))
            elif source == 'contratar':
                tasks.append(self._search_contratar(query, filters))
            elif source == 'bac':
                tasks.append(self._search_bac(query, filters))
            elif source in ['comprar_mendoza', 'compras_mendoza']:
                if not any(t.__name__ == '_search_mendoza' for t in tasks):
                    tasks.append(self._search_mendoza(query, filters))
        
        results = []
        for result in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(result, Exception):
                logger.error(f"Error en búsqueda: {str(result)}")
                continue
            results.extend(result)
        
        return results
