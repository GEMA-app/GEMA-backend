"""Middleware de rate limiting que limita el número de solicitudes
por dirección IP usando Redis como almacén de contadores.

Implementado como ASGI puro para evitar tareas anyio internas que
BaseHTTPMiddleware crea y que contaminan el event loop entre tests.
"""

import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.types import ASGIApp, Receive, Scope, Send

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers import jsonapi_response

logger = logging.getLogger(__name__)

LUA_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class RateLimitMiddleware:
    """Middleware ASGI de limitación de tasa (Rate Limiting) con Redis."""

    def __init__(
        self,
        app: ASGIApp,
        redis_client: Redis,
        rate_limits: dict[str, int] | None = None,
    ) -> None:
        """Inicializa el middleware con el cliente Redis y registra el script Lua."""
        self.app = app
        self.redis_client = redis_client
        self.rate_limit_script = redis_client.register_script(LUA_SCRIPT)
        self.rate_limits = rate_limits or {
            "/auth/login": 5,
            "/auth/register": 3,
            "/auth/refresh": 10,
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Aplica limitación de tasa a los endpoints configurados."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "").rstrip("/")

        limit = None
        for suffix, route_limit in self.rate_limits.items():
            if path.endswith(suffix):
                limit = route_limit
                break

        if limit is not None:
            # Extraer IP del cliente
            headers = dict(scope.get("headers", []))
            forwarded = headers.get(b"x-forwarded-for", b"").decode()
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()
            else:
                client = scope.get("client")
                client_ip = client[0] if client else "127.0.0.1"

            key = f"rate_limit:{path}:{client_ip}"

            try:
                current = await self.rate_limit_script(keys=[key], args=[60])
                if current > limit:
                    error = ErrorObject(
                        status="429",
                        code="ERR_TOO_MANY_REQUESTS",
                        title="Demasiadas solicitudes",
                        detail=f"Has excedido el límite de {limit} solicitudes por minuto.",
                    )
                    response = jsonapi_response(429, [error])
                    await response(scope, receive, send)
                    return
            except RedisError as e:
                logger.error("rate_limit_redis_unavailable: %s", e, extra={"path": path})

        await self.app(scope, receive, send)
