"""Excepciones del módulo de activos (no encontrado, código duplicado, serial duplicado)."""

from app.domain.exceptions.base import DomainException


class AssetException(DomainException):
    """Clase base para excepciones del módulo de activos."""

    pass


class AssetNotFoundError(AssetException):
    """Lanzada cuando un activo no es encontrado."""

    pass


class AssetCodeExistsError(AssetException):
    """Lanzada cuando se intenta registrar un activo con un código que ya existe en la empresa."""

    pass


class AssetSerialExistsError(AssetException):
    """Lanzada cuando se intenta registrar un activo con un número de serie
    que ya existe en la empresa.
    """

    pass


class AssetInvalidTransitionError(AssetException):
    """Lanzada cuando se intenta una transición de estado no permitida."""

    pass


class EmptySerialError(AssetException):
    """Lanzada cuando el número de serie del activo está vacío."""

    pass


class EmptyAssetCodeError(AssetException):
    """Lanzada cuando el código del activo está vacío."""

    pass
