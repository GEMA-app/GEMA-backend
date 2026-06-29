"""Excepción de dominio para datos desactualizados (Optimistic Locking)."""

from app.domain.exceptions.base import DomainException


class StaleDataError(DomainException):
    """Excepción lanzada cuando los datos del recurso están desactualizados (Optimistic Locking)."""

    pass
