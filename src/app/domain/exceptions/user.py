"""Excepciones de dominio para el módulo de Usuarios."""

from app.domain.exceptions.base import DomainException


class UserException(DomainException):
    """Clase base para excepciones exclusivas de la gestión y administración de usuarios."""
    pass

class UserNotFoundError(UserException):
    """Lanzada cuando se consulta un usuario por su ID y no existe en el sistema."""
    pass
