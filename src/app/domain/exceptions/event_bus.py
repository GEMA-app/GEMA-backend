"""Excepciones para errores al publicar eventos de dominio en el bus."""

from app.domain.exceptions.base import DomainException


class EventBusError(DomainException):
    """Clase base para excepciones del bus de eventos de dominio."""

    pass


class EventPublishError(EventBusError):
    """Se lanza cuando falla la publicación de eventos de dominio después del commit."""
