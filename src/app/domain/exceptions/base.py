"""Excepción base y ValidationError para la jerarquía de errores del dominio."""


class DomainException(Exception):
    """Clase base para todas las excepciones del dominio."""

    pass


class ValidationError(DomainException):
    """Lanzada cuando una validación de invariante de negocio falla."""

    pass
