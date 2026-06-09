"""Excepciones del módulo de roles (no encontrado, nombre duplicado, nombre vacío)."""

from app.domain.exceptions.base import DomainException


class RoleException(DomainException):
    """Clase base para excepciones del módulo de roles."""

    pass


class RoleNotFoundError(RoleException):
    """Lanzada cuando un rol no es encontrado."""

    pass


class RoleNameExistsError(RoleException):
    """Lanzada cuando se intenta crear un rol con un nombre que ya existe en la empresa."""

    pass


class EmptyRoleNameError(RoleException):
    """Se lanza cuando el nombre de un rol está vacío."""

    pass
