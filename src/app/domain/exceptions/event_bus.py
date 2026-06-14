"""Excepción para errores al publicar eventos de dominio en el bus."""

from app.domain.exceptions.base import DomainException


class EventPublishError(DomainException):
    """Se lanza cuando falla la publicación de eventos de dominio después del commit."""
