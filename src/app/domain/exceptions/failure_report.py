"""Excepciones del módulo de reportes de falla."""

from app.domain.exceptions.base import DomainException


class FailureReportException(DomainException):
    """Clase base para excepciones del módulo de reportes de falla."""

    pass


class EmptyTitleError(FailureReportException):
    """Lanzada cuando el título del reporte está vacío."""

    pass


class EmptyDescriptionError(FailureReportException):
    """Lanzada cuando la descripción del reporte está vacía."""

    pass


class EmptyLocationError(FailureReportException):
    """Lanzada cuando la ubicación del reporte está vacía."""

    pass


class EmptyReportedByError(FailureReportException):
    """Lanzada cuando el reportante del reporte está vacío."""

    pass


class FailureReportNotFoundError(FailureReportException):
    """Lanzada cuando un reporte de falla no es encontrado."""

    pass


class FailureReportInvalidTransitionError(FailureReportException):
    """Lanzada cuando se intenta una transición de estado no permitida."""

    pass
