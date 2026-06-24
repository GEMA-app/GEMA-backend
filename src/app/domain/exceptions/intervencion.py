"""Excepciones del módulo de intervenciones técnicas."""


class IntervencionException(Exception):
    """Excepción base para errores del módulo de intervenciones."""


class IntervencionNotFoundError(IntervencionException):
    """Se lanza cuando una intervención no existe."""


class IntervencionInvalidTransitionError(IntervencionException):
    """Se lanza cuando se intenta hacer una transición de estado inválida."""


class IntervencionInvalidDataError(IntervencionException):
    """Se lanza cuando los datos de la intervención no son válidos."""