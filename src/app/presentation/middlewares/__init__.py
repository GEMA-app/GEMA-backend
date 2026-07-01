"""Middlewares de la capa de presentación.

Proporciona middlewares ASGI para:
- Correlation ID (request_id)
- Validación de Content-Type y Accept headers
- Rate limiting por IP
"""

from app.presentation.middlewares.accept import AcceptMiddleware
from app.presentation.middlewares.content_type import ContentTypeMiddleware
from app.presentation.middlewares.rate_limit import RateLimitMiddleware
from app.presentation.middlewares.request_id import RequestIdMiddleware

__all__ = [
    "AcceptMiddleware",
    "ContentTypeMiddleware",
    "RateLimitMiddleware",
    "RequestIdMiddleware",
]
