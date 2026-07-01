"""Excepciones de dominio para el módulo de Proveedores."""

from app.domain.exceptions.base import DomainException


class SupplierException(DomainException):
    """Clase base para excepciones del módulo de proveedores."""
    pass


class SupplierNotFoundError(SupplierException):
    """Lanzada cuando no se encuentra el proveedor solicitado."""
    pass


class SupplierRifExistsError(SupplierException):
    """Lanzada cuando ya existe un proveedor con el mismo RIF en la empresa."""
    pass


class SupplierHasInventoryPartsError(SupplierException):
    """Lanzada cuando se intenta eliminar un proveedor con repuestos asociados."""
    pass
