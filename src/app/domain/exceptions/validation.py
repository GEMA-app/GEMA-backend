"""Excepciones de validación de dominio (UUID inválido, slug inválido)."""

from app.domain.exceptions.base import DomainException


class ValidationException(DomainException):
    """Lanzada cuando una validación de reglas de negocio en la capa de aplicación falla."""

    pass


class InvalidUUIDError(ValidationException):
    """Se lanza cuando un identificador UUID tiene formato inválido."""

    pass


class InvalidSlugError(ValidationException):
    """Se lanza cuando un slug tiene formato inválido."""

    pass
