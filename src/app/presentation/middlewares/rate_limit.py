import logging
from typing import Any

from fastapi import status
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

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


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitación de tasa (Rate Limiting) con Redis."""

    def __init__(
        self,
        app: Any,
        redis_client: Any,
        rate_limits: dict[str, int] | None = None,
    ) -> None:
        """Inicializa el middleware con el cliente Redis y registra el script Lua."""
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit_script = redis_client.register_script(LUA_SCRIPT)
        self.rate_limits = rate_limits or {
            "/auth/login": 5,
            "/auth/register": 3,
            "/auth/refresh": 10,
        }

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Aplica limitación de tasa a los endpoints configurados."""
        path = request.url.path.rstrip("/")  # Normalizar trailing slash

        limit = None
        for suffix, route_limit in self.rate_limits.items():
            if path.endswith(suffix):
                limit = route_limit
                break

        if limit is not None:
            client_ip = request.headers.get("X-Forwarded-For")
            if client_ip:
                client_ip = client_ip.split(",")[0].strip()
            else:
                client_ip = request.client.host if request.client else "127.0.0.1"

            key = f"rate_limit:{path}:{client_ip}"

            try:
                current = await self.rate_limit_script(keys=[key], args=[60])
                if current > limit:
                    error = ErrorObject(
                        status=str(status.HTTP_429_TOO_MANY_REQUESTS),
                        code="ERR_TOO_MANY_REQUESTS",
                        title="Demasiadas solicitudes",
                        detail=f"Has excedido el límite de {limit} solicitudes por minuto.",
                    )
                    return jsonapi_response(status.HTTP_429_TOO_MANY_REQUESTS, [error])
            except RedisError as e:
                logger.error("rate_limit_redis_unavailable: %s", e, extra={"path": path})

        response: Response = await call_next(request)
        return response
