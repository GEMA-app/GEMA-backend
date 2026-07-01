"""Adaptador del limitador de tasa utilizando Redis y scripts Lua."""

import redis
import structlog

from app.application.ports.rate_limiter import RateLimiterPort
from app.infrastructure.cache.redis import redis_client

logger = structlog.get_logger()

EMAIL_LUA_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class RedisRateLimiter(RateLimiterPort):
    """Implementación de RateLimiterPort que ejecuta lógica de límites en Redis."""

    def __init__(self) -> None:
        """Inicializa el rate limiter registrando el script Lua de Redis."""
        self._script = redis_client.register_script(EMAIL_LUA_SCRIPT)

    async def is_rate_limited(self, key: str, limit: int, window_seconds: int) -> bool:
        """Verifica el límite de tasa usando un script de incremento atómico en Redis.

        Args:
            key: Llave identificadora en Redis.
            limit: Límite máximo de peticiones.
            window_seconds: TTL de la ventana en segundos.

        Returns:
            True si excede el límite, False en caso de error o si está dentro
            del límite (fail-open).
        """
        try:
            current = await self._script(keys=[key], args=[str(window_seconds)])
            return int(current) > limit
        except redis.RedisError as e:
            logger.error("redis_rate_limit_error", key=key, error=str(e))
            return False  # Fail-open por diseño de tolerancia a fallos
