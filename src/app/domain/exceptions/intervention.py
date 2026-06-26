"""Excepciones del módulo de intervenciones técnicas."""

from app.domain.exceptions.base import DomainException


class InterventionException(DomainException):
    """Excepción base para errores del módulo de intervenciones."""


class InterventionNotFoundError(InterventionException):
    """Se lanza cuando una intervención no existe."""


class InterventionInvalidTransitionError(InterventionException):
    """Se lanza cuando se intenta hacer una transición de estado inválida."""


class InterventionInvalidDataError(InterventionException):
    """Se lanza cuando los datos de la intervención no son válidos."""
