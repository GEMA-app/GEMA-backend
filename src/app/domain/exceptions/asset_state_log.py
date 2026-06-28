"""Excepciones del módulo AssetStateLog."""

from app.domain.exceptions.base import DomainException


class AssetStateLogException(DomainException):
    """Clase base para excepciones del módulo de historial de estados."""

    pass


class AssetStateLogNotFoundError(AssetStateLogException):
    """Lanzada cuando un registro de cambio de estado no es encontrado."""

    pass
