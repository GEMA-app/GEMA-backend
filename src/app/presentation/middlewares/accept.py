from typing import Any

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers import jsonapi_response


class AcceptMiddleware(BaseHTTPMiddleware):
    """Middleware que valida el encabezado Accept para garantizar la compatibilidad con JSON:API."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        accept = request.headers.get("Accept", "*/*")
        if (
            "application/vnd.api+json" not in accept
            and "*/*" not in accept
            and "application/json" not in accept
        ):
            error = ErrorObject(
                status=str(status.HTTP_406_NOT_ACCEPTABLE),
                code="ERR_NOT_ACCEPTABLE",
                title="Encabezado Accept no aceptable",
                detail="El servidor solo puede generar respuestas con Content-Type: application/vnd.api+json.",
            )
            return jsonapi_response(status.HTTP_406_NOT_ACCEPTABLE, [error])

        response: Response = await call_next(request)
        return response
