import redis
import zlib
import pickle
import time
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass
import logging
from .logging_config import setup_logging

logger = setup_logging()

class CacheTier(Enum):
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"

@dataclass
class CacheConfig:
    compression_threshold: int = 1024  # Bytes
    compression_level: int = 6  # 0-9, higher means better compression but slower
    memory_cache_size: int = 1000  # Number of items
    default_ttl: int = 3600  # 1 hour
    priority_ttls: Dict[str, int] = None

class CacheManager:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
        self.memory_cache: Dict[str, Dict] = {}
        self.access_counts: Dict[str, int] = {}
        self.last_cleanup = time.time()
        
    def _compress_data(self, data: bytes) -> bytes:
        """Comprime datos si superan el umbral de tamaño."""
        if len(data) > self.config.compression_threshold:
            return zlib.compress(data, level=self.config.compression_level)
        return data

    def _decompress_data(self, data: bytes) -> bytes:
        """Intenta descomprimir datos si están comprimidos."""
        try:
            return zlib.decompress(data)
        except zlib.error:
            return data

    def _serialize(self, value: Any) -> bytes:
        """Serializa y opcionalmente comprime los datos."""
        serialized = pickle.dumps(value)
        return self._compress_data(serialized)

    def _deserialize(self, value: bytes) -> Any:
        """Descomprime y deserializa los datos."""
        decompressed = self._decompress_data(value)
        return pickle.loads(decompressed)

    def _get_ttl(self, key: str) -> int:
        """Determina el TTL basado en la prioridad del contenido."""
        if self.config.priority_ttls and any(p in key for p in self.config.priority_ttls):
            for priority, ttl in self.config.priority_ttls.items():
                if priority in key:
                    return ttl
        return self.config.default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché usando un sistema de niveles."""
        # Incrementar contador de accesos
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        
        # Verificar caché en memoria
        if key in self.memory_cache:
            logger.debug(f"Cache hit (memory): {key}")
            return self.memory_cache[key]['value']
        
        # Verificar caché en Redis
        try:
            data = self.redis_client.get(key)
            if data:
                value = self._deserialize(data)
                # Promover a caché en memoria si es accedido frecuentemente
                if self.access_counts[key] > 5:
                    self._promote_to_memory(key, value)
                logger.debug(f"Cache hit (redis): {key}")
                return value
        except Exception as e:
            logger.error(f"Error accessing Redis cache: {str(e)}")
        
        return None

    def set(self, key: str, value: Any, tier: CacheTier = CacheTier.REDIS) -> None:
        """Almacena un valor en el caché."""
        ttl = self._get_ttl(key)
        
        try:
            if tier == CacheTier.MEMORY or self.access_counts.get(key, 0) > 5:
                self._promote_to_memory(key, value)
            
            if tier == CacheTier.REDIS:
                serialized = self._serialize(value)
                self.redis_client.setex(key, ttl, serialized)
            
            logger.debug(f"Cache set: {key} (tier: {tier.value})")
            
            # Ejecutar limpieza si es necesario
            self._cleanup_if_needed()
            
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")

    def _promote_to_memory(self, key: str, value: Any) -> None:
        """Promueve un valor al caché en memoria."""
        if len(self.memory_cache) >= self.config.memory_cache_size:
            self._evict_from_memory()
        
        self.memory_cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'access_count': self.access_counts.get(key, 0)
        }

    def _evict_from_memory(self) -> None:
        """Elimina elementos del caché en memoria según la política LRU."""
        if not self.memory_cache:
            return
            
        # Encontrar el elemento menos recientemente usado
        lru_key = min(self.memory_cache.items(),
                     key=lambda x: (x[1]['access_count'], x[1]['timestamp']))[0]
        del self.memory_cache[lru_key]

    def _cleanup_if_needed(self) -> None:
        """Ejecuta limpieza periódica del caché."""
        current_time = time.time()
        if current_time - self.last_cleanup > 3600:  # Cada hora
            self._cleanup()
            self.last_cleanup = current_time

    def _cleanup(self) -> None:
        """Limpia entradas expiradas y optimiza el uso de memoria."""
        # Limpiar caché en memoria
        current_time = time.time()
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if current_time - v['timestamp'] > self._get_ttl(k)
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Limpiar contadores de acceso antiguos
        old_keys = [
            k for k, count in self.access_counts.items()
            if k not in self.memory_cache and count < 5
        ]
        for key in old_keys:
            del self.access_counts[key]
        
        logger.info(f"Cache cleanup completed. Removed {len(expired_keys)} expired items.")

    def invalidate(self, key: str) -> None:
        """Invalida una entrada específica del caché."""
        if key in self.memory_cache:
            del self.memory_cache[key]
        self.redis_client.delete(key)
        logger.debug(f"Cache invalidated: {key}")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del sistema de caché."""
        return {
            'memory_cache_size': len(self.memory_cache),
            'memory_cache_limit': self.config.memory_cache_size,
            'access_counts': len(self.access_counts),
            'compression_enabled': self.config.compression_threshold > 0,
            'compression_level': self.config.compression_level
        }
