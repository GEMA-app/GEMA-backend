"""Paquete de handlers de eventos de dominio."""

from app.infrastructure.events.handlers.notifications import (
    handle_password_changed,
    handle_password_reset_completed,
    handle_password_reset_initiated,
    handle_user_registered,
)

__all__ = [
    "handle_user_registered",
    "handle_password_changed",
    "handle_password_reset_initiated",
    "handle_password_reset_completed",
]
