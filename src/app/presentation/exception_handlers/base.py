from collections.abc import Mapping

from fastapi.responses import JSONResponse

from app.presentation.api.v1.schemas.jsonapi_base import (
    ErrorObject,
    JsonApiErrorDocument,
)


def jsonapi_response(
    status_code: int, errors: list[ErrorObject], headers: Mapping[str, str] | None = None
) -> JSONResponse:
    """Genera una respuesta JSONResponse formateada bajo la especificación JSON:API."""
    doc = JsonApiErrorDocument(errors=errors)
    return JSONResponse(
        status_code=status_code,
        content=doc.model_dump(exclude_none=True),
        headers={"Content-Type": "application/vnd.api+json", **(headers or {})},
    )
