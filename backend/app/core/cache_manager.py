from typing import Any, Optional, Union, Dict
import ioredis
import json
from datetime import timedelta
import hashlib
import logging
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(
        self,
        redis_url: str,
        default_ttl: int = 3600,  # 1 hora por defecto
        prefix: str = "licitometro:"
    ):
        self.redis = ioredis.from_url(redis_url)
        self.default_ttl = default_ttl
        self.prefix = prefix

    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        try:
            full_key = f"{self.prefix}{key}"
            value = await self.redis.get(full_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error al obtener del caché: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Guarda un valor en el caché"""
        try:
            full_key = f"{self.prefix}{key}"
            ttl = ttl if ttl is not None else self.default_ttl
            await self.redis.set(
                full_key,
                json.dumps(value),
                'EX',
                ttl
            )
            return True
        except Exception as e:
            logger.error(f"Error al guardar en caché: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Elimina una clave del caché"""
        try:
            full_key = f"{self.prefix}{key}"
            await self.redis.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Error al eliminar del caché: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Elimina todas las claves que coincidan con un patrón"""
        try:
            full_pattern = f"{self.prefix}{pattern}"
            cursor = '0'
            while cursor != 0:
                cursor, keys = await self.redis.scan(
                    cursor,
                    match=full_pattern,
                    count=100
                )
                if keys:
                    await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error al limpiar caché por patrón: {e}")
            return False

    def cached(
        self,
        key_prefix: str,
        ttl: Optional[int] = None,
        key_builder: Optional[callable] = None
    ):
        """Decorador para cachear resultados de funciones"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Construir clave de caché
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    # Crear hash de los argumentos
                    args_str = json.dumps(
                        (args, kwargs),
                        sort_keys=True,
                        default=str
                    )
                    args_hash = hashlib.md5(
                        args_str.encode()
                    ).hexdigest()
                    cache_key = f"{key_prefix}:{args_hash}"

                # Intentar obtener del caché
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Ejecutar función y cachear resultado
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result

            return wrapper
        return decorator

    async def get_or_compute(
        self,
        key: str,
        compute_func: callable,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Any:
        """Obtiene un valor del caché o lo computa si no existe"""
        if not force_refresh:
            cached_value = await self.get(key)
            if cached_value is not None:
                return cached_value

        # Computar nuevo valor
        value = await compute_func()
        await self.set(key, value, ttl)
        return value

    async def bulk_get(self, keys: list[str]) -> Dict[str, Any]:
        """Obtiene múltiples valores del caché"""
        try:
            full_keys = [f"{self.prefix}{key}" for key in keys]
            values = await self.redis.mget(*full_keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error(f"Error en bulk_get: {e}")
            return {}

    async def bulk_set(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Guarda múltiples valores en el caché"""
        try:
            pipeline = self.redis.pipeline()
            for key, value in items.items():
                full_key = f"{self.prefix}{key}"
                pipeline.set(
                    full_key,
                    json.dumps(value),
                    'EX',
                    ttl if ttl is not None else self.default_ttl
                )
            await pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Error en bulk_set: {e}")
            return False

    async def increment(
        self,
        key: str,
        amount: int = 1,
        ttl: Optional[int] = None
    ) -> Optional[int]:
        """Incrementa un contador en el caché"""
        try:
            full_key = f"{self.prefix}{key}"
            pipeline = self.redis.pipeline()
            pipeline.incrby(full_key, amount)
            if ttl is not None:
                pipeline.expire(full_key, ttl)
            result = await pipeline.execute()
            return result[0]
        except Exception as e:
            logger.error(f"Error al incrementar contador: {e}")
            return None

    async def close(self):
        """Cierra la conexión con Redis"""
        await self.redis.quit()
