"""Middleware que inyecta un ID de correlación único (UUID) en cada
solicitud entrante y lo propaga a la respuesta.

Implementado como ASGI puro para evitar tareas anyio internas que
BaseHTTPMiddleware crea y que contaminan el event loop entre tests.
"""

import uuid
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestIdMiddleware:
    """Middleware ASGI que inyecta un identificador único de correlación (UUID)
    en cada solicitud.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Inicializa el middleware con la app ASGI interna."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Ejecuta la inyección del ID de correlación en la solicitud."""
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", b"").decode() or str(uuid.uuid4())

        # Almacenar en scope.state para que los endpoints puedan accederlo
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers: list[Any] = list(message.get("headers", []))
                response_headers.append([b"x-request-id", request_id.encode()])
                message["headers"] = response_headers
            await send(message)

        await self.app(scope, receive, send_with_request_id)
