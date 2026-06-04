from typing import Any

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers import jsonapi_response


class ContentTypeMiddleware(BaseHTTPMiddleware):
    """Middleware que valida el encabezado Content-Type de JSON:API."""

    def __init__(self, app: Any, strict_jsonapi: bool = True) -> None:
        """Inicializa el middleware con la configuración de JSON:API estricto."""
        super().__init__(app)
        self.strict_jsonapi = strict_jsonapi

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Procesa y valida las peticiones entrantes."""
        if request.method in ("POST", "PATCH", "DELETE"):
            content_type = request.headers.get("Content-Type", "")
            expected = "application/vnd.api+json"
            json_type = "application/json"

            if self.strict_jsonapi:
                if expected not in content_type and json_type not in content_type:
                    detail_msg = (
                        f"Se requiere Content-Type: {expected} o {json_type} "
                        "en modo estricto."
                    )
                    error = ErrorObject(
                        status=str(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE),
                        code="ERR_UNSUPPORTED_MEDIA_TYPE",
                        title="Tipo de contenido no soportado",
                        detail=detail_msg,
                    )
                    return jsonapi_response(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, [error])
            else:
                if expected not in content_type and json_type not in content_type:
                    error = ErrorObject(
                        status=str(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE),
                        code="ERR_UNSUPPORTED_MEDIA_TYPE",
                        title="Tipo de contenido no soportado",
                        detail=f"Se requiere Content-Type: {expected} o {json_type}.",
                    )
                    return jsonapi_response(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, [error])

        response: Response = await call_next(request)
        return response
