"""Excepciones de dominio para el sistema de notificaciones de GEMA."""

from app.domain.exceptions.base import DomainException


class NotificationError(DomainException):
    """Se lanza cuando ocurre un error al enviar una notificación o correo SMTP."""


class TemplateNotFoundError(DomainException):
    """Se lanza cuando una plantilla de correo/notificación solicitada no existe."""
