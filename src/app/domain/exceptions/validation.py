from app.domain.exceptions.base import DomainException


class ValidationException(DomainException):
    """Lanzada cuando una validación de reglas de negocio en la capa de aplicación fallan."""

    pass
