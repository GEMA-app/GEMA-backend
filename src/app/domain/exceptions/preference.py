"""Excepciones del módulo de preferencias de usuario."""

from app.domain.exceptions.base import DomainException


class PreferenceException(DomainException):
    """Clase base para excepciones del módulo de preferencias."""

    pass


class PreferenceNotFoundError(PreferenceException):
    """Lanzada cuando no se encuentran preferencias para un usuario."""

    pass


class PreferenceThemeInvalidError(PreferenceException):
    """Lanzada cuando se intenta establecer un tema no válido."""

    pass
