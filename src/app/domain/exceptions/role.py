from app.domain.exceptions.base import DomainException
from app.domain.exceptions.validation import ValidationException


class RoleException(DomainException):
    """Clase base para excepciones del módulo de roles."""

    pass


class RoleNotFoundError(RoleException):
    """Lanzada cuando un rol no es encontrado."""

    pass


class RoleNameExistsError(RoleException):
    """Lanzada cuando se intenta crear un rol con un nombre que ya existe en la empresa."""

    pass


class EmptyRoleNameError(RoleException, ValidationException):
    """Se lanza cuando el nombre de un rol está vacío."""

    pass
