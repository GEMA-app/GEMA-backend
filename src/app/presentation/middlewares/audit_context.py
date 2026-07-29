"""ASGI middleware que inyecta la IP del cliente en contextvar."""

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.infrastructure.context import client_ip


class AuditContextMiddleware(BaseHTTPMiddleware):
    """Middleware que extrae la IP del cliente y la inyecta en contextvar."""

    async def dispatch(  # noqa: D102
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Procesa el request extrayendo y almacenando la IP del cliente."""
        ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else None)
            or "unknown"
        )
        token = client_ip.set(ip)
        try:
            return await call_next(request)
        finally:
            client_ip.reset(token)
