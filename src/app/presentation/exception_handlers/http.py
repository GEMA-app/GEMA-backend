from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers.base import jsonapi_response


async def starlette_http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Mapea excepciones HTTP genéricas de Starlette al formato JSON:API."""
    assert isinstance(exc, StarletteHTTPException)
    error = ErrorObject(
        status=str(exc.status_code),
        code=f"HTTP_{exc.status_code}",
        title=exc.detail,
        detail=exc.detail,
    )
    return jsonapi_response(exc.status_code, [error], headers=exc.headers)
