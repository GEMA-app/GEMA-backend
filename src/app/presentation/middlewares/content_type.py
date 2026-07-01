"""Middleware que valida el Content-Type de las solicitudes entrantes
y fuerza el tipo application/vnd.api+json para endpoints JSON:API.

Implementado como ASGI puro para evitar tareas anyio internas que
BaseHTTPMiddleware crea y que contaminan el event loop entre tests.
"""

from starlette.types import ASGIApp, Receive, Scope, Send

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers import jsonapi_response


class ContentTypeMiddleware:
    """Middleware ASGI que valida el encabezado Content-Type de JSON:API."""

    def __init__(self, app: ASGIApp, strict_jsonapi: bool = True) -> None:
        """Inicializa el middleware con la configuración de JSON:API estricto."""
        self.app = app
        self.strict_jsonapi = strict_jsonapi

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Procesa y valida las peticiones entrantes."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "")
        if method in ("POST", "PATCH"):
            headers = dict(scope.get("headers", []))
            content_type = headers.get(b"content-type", b"").decode()
            expected = "application/vnd.api+json"
            json_type = "application/json"

            if expected not in content_type and json_type not in content_type:
                detail_msg: str
                if self.strict_jsonapi:
                    detail_msg = (
                        f"Se requiere Content-Type: {expected} o {json_type} en modo estricto."
                    )
                else:
                    detail_msg = f"Se requiere Content-Type: {expected} o {json_type}."
                error = ErrorObject(
                    status="415",
                    code="ERR_UNSUPPORTED_MEDIA_TYPE",
                    title="Tipo de contenido no soportado",
                    detail=detail_msg,
                )
                response = jsonapi_response(415, [error])
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
