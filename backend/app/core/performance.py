import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 60
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self._state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    @property
    def state(self) -> str:
        return self._state

    async def _should_allow_request(self) -> bool:
        """Determina si se debe permitir una solicitud"""
        async with self._lock:
            now = datetime.utcnow()
            
            if self._state == "open":
                # Verificar si debemos intentar half-open
                if self.last_failure_time and (
                    now - self.last_failure_time
                ).total_seconds() >= self.reset_timeout:
                    self._state = "half-open"
                    return True
                return False
                
            elif self._state == "half-open":
                # Solo permitir una solicitud en estado half-open
                return True
                
            return True  # Estado closed

    async def _handle_success(self):
        """Maneja una solicitud exitosa"""
        async with self._lock:
            if self._state == "half-open":
                self._state = "closed"
            self.failures = 0
            self.last_failure_time = None

    async def _handle_failure(self):
        """Maneja una solicitud fallida"""
        async with self._lock:
            self.failures += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failures >= self.failure_threshold:
                self._state = "open"
                logger.warning(
                    f"Circuit breaker {self.name} opened after "
                    f"{self.failures} failures"
                )

    @asynccontextmanager
    async def __aenter__(self):
        """Context manager para usar el circuit breaker"""
        if not await self._should_allow_request():
            raise Exception(
                f"Circuit breaker {self.name} is {self._state}"
            )
        
        try:
            yield self
            await self._handle_success()
        except Exception as e:
            await self._handle_failure()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class RateLimiter:
    def __init__(
        self,
        rate: int,
        period: int = 60,
        burst: Optional[int] = None
    ):
        """
        Args:
            rate: Número máximo de solicitudes por periodo
            period: Periodo en segundos
            burst: Tamaño del burst (opcional)
        """
        self.rate = rate
        self.period = period
        self.burst = burst or rate
        self._allowance = rate
        self._last_check = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """
        Adquiere tokens del rate limiter
        
        Args:
            tokens: Número de tokens a adquirir
            
        Raises:
            Exception: Si no hay suficientes tokens disponibles
        """
        async with self._lock:
            now = time.monotonic()
            time_passed = now - self._last_check
            self._last_check = now
            
            # Rellenar tokens basado en el tiempo transcurrido
            self._allowance += time_passed * (self.rate / self.period)
            
            # No exceder el límite de burst
            if self._allowance > self.burst:
                self._allowance = self.burst
            
            # Verificar si hay suficientes tokens
            if self._allowance < tokens:
                wait_time = (tokens - self._allowance) * (
                    self.period / self.rate
                )
                raise Exception(
                    f"Rate limit exceeded. Try again in {wait_time:.2f}s"
                )
            
            self._allowance -= tokens

    @asynccontextmanager
    async def limit(self, tokens: int = 1):
        """Context manager para rate limiting"""
        await self.acquire(tokens)
        try:
            yield
        finally:
            pass  # No necesitamos liberar tokens
