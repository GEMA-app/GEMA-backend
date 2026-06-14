"""Middleware que inyecta un ID de correlación único (UUID) en cada
solicitud entrante y lo propaga a la respuesta.
"""

import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware que inyecta un identificador único de correlación (UUID) en cada solicitud."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Ejecuta la inyección del ID de correlación en la solicitud."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
