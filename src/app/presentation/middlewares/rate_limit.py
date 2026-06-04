import logging
from typing import Any

from fastapi import status
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.infrastructure.cache.redis import redis_client
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

rate_limit_script = redis_client.register_script(LUA_SCRIPT)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitación de tasa (Rate Limiting) con script Lua atómico en Redis y comportamiento fail-open."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        path = request.url.path

        limit = None
        if path.endswith("/auth/login"):
            limit = 5
        elif path.endswith("/auth/register"):
            limit = 3
        elif path.endswith("/auth/refresh"):
            limit = 10

        if limit is not None:
            client_ip = request.headers.get("X-Forwarded-For")
            if client_ip:
                client_ip = client_ip.split(",")[0].strip()
            else:
                client_ip = request.client.host if request.client else "127.0.0.1"

            key = f"rate_limit:{path}:{client_ip}"

            try:
                current = await rate_limit_script(keys=[key], args=[60])
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
