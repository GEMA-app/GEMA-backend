"""Excepciones de dominio para el módulo de órdenes de trabajo."""

from app.domain.exceptions.base import DomainException


class WorkOrderException(DomainException):
    """Excepción base para errores relacionados con órdenes de trabajo."""


class WorkOrderNotFoundError(WorkOrderException):
    """Excepción lanzada cuando no se encuentra una orden de trabajo."""


class WorkOrderCodeExistsError(WorkOrderException):
    """Excepción lanzada cuando el código de orden de trabajo ya existe en la empresa."""


class WorkOrderInvalidStateError(WorkOrderException):
    """Excepción lanzada cuando se intenta una transición de estado no válida."""


class WorkOrderInvalidDataError(WorkOrderException):
    """Excepción lanzada cuando los datos proporcionados para la orden son inválidos."""
