from app.domain.exceptions.base import DomainException


class LocationException(DomainException):
    """Clase base para excepciones del módulo de ubicaciones."""

    pass


class LocationNotFoundError(LocationException):
    """Lanzada cuando una ubicación no es encontrada."""

    pass


class LocationCircularReferenceError(LocationException):
    """Lanzada cuando se detecta una referencia circular en la jerarquía de ubicaciones."""

    pass


class LocationInvalidTypeHierarchyError(LocationException):
    """Lanzada cuando se intenta establecer una relación de jerarquía inválida entre tipos de ubicación."""

    pass
