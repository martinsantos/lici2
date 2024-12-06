from typing import Dict, Any, Optional
import time
import logging
import psutil
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_tasks: int
    cache_hits: int
    cache_misses: int
    avg_response_time: float
    error_count: int
    timestamp: str

class MetricsCollector:
    def __init__(self, metrics_port: int = 9090):
        # Prometheus metrics
        self.task_counter = Counter('recon_tasks_total', 'Total number of tasks processed')
        self.active_tasks = Gauge('recon_active_tasks', 'Number of currently active tasks')
        self.cache_hits = Counter('recon_cache_hits_total', 'Total number of cache hits')
        self.cache_misses = Counter('recon_cache_misses_total', 'Total number of cache misses')
        self.response_time = Histogram('recon_response_time_seconds', 'Task response time in seconds')
        self.error_counter = Counter('recon_errors_total', 'Total number of errors')
        
        # System metrics
        self.system_cpu = Gauge('system_cpu_usage', 'System CPU usage')
        self.system_memory = Gauge('system_memory_usage', 'System memory usage')
        self.system_disk = Gauge('system_disk_usage', 'System disk usage')
        
        # User and feedback metrics
        self.user_errors = Counter('recon_user_errors_total', 'Total number of user-facing errors',
                                 ['error_type'])
        self.user_feedback = Counter('recon_user_feedback_total', 'User feedback metrics',
                                   ['feedback_type'])
        self.task_success_rate = Gauge('recon_task_success_rate', 'Task success rate percentage')
        
        # Logger configuration
        self.logger = logging.getLogger('recon_metrics')
        self.setup_logger()
        
        # Start Prometheus metrics server
        start_http_server(metrics_port)
        
        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def setup_logger(self):
        """Configura el logger con formato detallado para trazabilidad."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(context)s'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler('recon_metrics.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    def log_with_context(self, level: str, message: str, context: Dict[str, Any]):
        """Registra un mensaje con contexto adicional."""
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra={'context': str(context)})

    def record_user_feedback(self, feedback_type: str, details: Dict[str, Any]):
        """Registra feedback del usuario."""
        self.user_feedback.labels(feedback_type=feedback_type).inc()
        self.log_with_context(
            'INFO',
            f'User feedback received: {feedback_type}',
            {'feedback_type': feedback_type, 'details': details}
        )

    def record_user_error(self, error_type: str, error_details: Dict[str, Any]):
        """Registra errores encontrados por usuarios."""
        self.user_errors.labels(error_type=error_type).inc()
        self.log_with_context(
            'ERROR',
            f'User error occurred: {error_type}',
            {'error_type': error_type, 'details': error_details}
        )

    def update_success_rate(self, success_count: int, total_count: int):
        """Actualiza la tasa de éxito de las tareas."""
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            self.task_success_rate.set(success_rate)
            self.log_with_context(
                'INFO',
                f'Task success rate updated: {success_rate}%',
                {'success_count': success_count, 'total_count': total_count}
            )

    def _monitor_system(self):
        while True:
            try:
                # Update system metrics
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                self.system_cpu.set(cpu)
                self.system_memory.set(memory)
                self.system_disk.set(disk)
                
                time.sleep(15)  # Update every 15 seconds
            except Exception as e:
                logger.error(f"Error monitoring system metrics: {str(e)}")
    
    def record_task_start(self):
        """Record the start of a new task"""
        self.task_counter.inc()
        self.active_tasks.inc()
    
    def record_task_complete(self):
        """Record task completion"""
        self.active_tasks.dec()
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits.inc()
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses.inc()
    
    def record_error(self):
        """Record an error occurrence"""
        self.error_counter.inc()
    
    @contextmanager
    def measure_time(self):
        """Context manager to measure execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.response_time.observe(duration)
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        return SystemMetrics(
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            active_tasks=self.active_tasks._value.get(),
            cache_hits=self.cache_hits._value.get(),
            cache_misses=self.cache_misses._value.get(),
            avg_response_time=sum(self.response_time._sum.values()) / max(sum(self.response_time._count.values()), 1),
            error_count=self.error_counter._value.get(),
            timestamp=datetime.now().isoformat()
        )

    def to_json(self) -> str:
        """Convert current metrics to JSON string"""
        return json.dumps(asdict(self.get_current_metrics()))

    def get_system_metrics(self) -> Dict[str, float]:
        """Recopila y retorna métricas del sistema."""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        self.system_cpu.set(cpu)
        self.system_memory.set(memory)
        self.system_disk.set(disk)
        
        return {
            'cpu_usage': cpu,
            'memory_usage': memory,
            'disk_usage': disk
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Genera un resumen completo de todas las métricas."""
        return {
            'tasks': {
                'total': self.task_counter._value.get(),
                'active': self.active_tasks._value.get(),
                'success_rate': self.task_success_rate._value.get()
            },
            'cache': {
                'hits': self.cache_hits._value.get(),
                'misses': self.cache_misses._value.get()
            },
            'user_feedback': {
                'errors': {k: v for k, v in self.user_errors._metrics.items()},
                'feedback': {k: v for k, v in self.user_feedback._metrics.items()}
            },
            'system': self.get_system_metrics()
        }
