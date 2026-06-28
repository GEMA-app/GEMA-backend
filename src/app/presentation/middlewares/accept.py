"""Middleware que valida el header Accept de las solicitudes entrantes
y rechaza peticiones que no acepten application/vnd.api+json.

Implementado como ASGI puro para evitar tareas anyio internas que
BaseHTTPMiddleware crea y que contaminan el event loop entre tests.
"""

from starlette.types import ASGIApp, Receive, Scope, Send

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers import jsonapi_response


class AcceptMiddleware:
    """Middleware ASGI que valida el encabezado Accept para garantizar la compatibilidad con JSON:API."""

    def __init__(self, app: ASGIApp) -> None:
        """Inicializa el middleware con la app ASGI interna."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Ejecuta la validación del encabezado Accept."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        accept = headers.get(b"accept", b"*/*").decode()

        if (
            "application/vnd.api+json" not in accept
            and "*/*" not in accept
            and "application/json" not in accept
        ):
            detail = (
                "El servidor solo puede generar respuestas con"
                " Content-Type: application/vnd.api+json."
            )
            error = ErrorObject(
                status="406",
                code="ERR_NOT_ACCEPTABLE",
                title="Encabezado Accept no aceptable",
                detail=detail,
            )
            response = jsonapi_response(406, [error])
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
