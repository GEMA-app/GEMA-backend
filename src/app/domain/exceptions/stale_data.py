from app.domain.exceptions.base import DomainException


class StaleDataError(DomainException):
    """Excepción lanzada cuando los datos del recurso están desactualizados (Optimistic Locking)."""

    pass
