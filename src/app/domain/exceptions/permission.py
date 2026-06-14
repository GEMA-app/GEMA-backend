"""Excepciones del módulo de permisos (permisos insuficientes)."""

from app.domain.exceptions.base import DomainException


class PermissionException(DomainException):
    """Clase base para excepciones de permisos."""

    pass


class InsufficientPermissionsError(PermissionException):
    """Lanzada cuando un usuario no tiene los permisos suficientes para realizar una acción."""

    pass
