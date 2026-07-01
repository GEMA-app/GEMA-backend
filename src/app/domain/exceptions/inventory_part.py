"""Excepciones de dominio para el módulo de inventario de repuestos (InventoryPart)."""

from app.domain.exceptions.base import DomainException


class InventoryPartException(DomainException):
    """Excepción base del módulo de inventario de repuestos."""
    pass


class InventoryPartNotFoundError(InventoryPartException):
    """Excepción lanzada cuando no se encuentra un repuesto en el inventario."""
    pass


class InvalidStockError(InventoryPartException):
    """Excepción lanzada cuando los valores de stock son inválidos (negativos o inconsistentes)."""
    pass


class InvalidPriceError(InventoryPartException):
    """Excepción lanzada cuando el precio unitario del repuesto es inválido."""
    pass


class EmptyStockLocationError(InventoryPartException):
    """Excepción lanzada cuando la ubicación del almacén está vacía."""
    pass
