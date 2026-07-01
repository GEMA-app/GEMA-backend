"""Servicio de notificaciones: envío de correos electrónicos."""

from app.infrastructure.notifications.email_sender import (
    SmtpNotificationSender,
)

__all__ = [
    "SmtpNotificationSender",
]
