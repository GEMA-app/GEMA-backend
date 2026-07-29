"""Contexto del request actual para auditoría y trazabilidad."""

from contextvars import ContextVar

current_user_id: ContextVar[str | None] = ContextVar("current_user_id", default=None)
client_ip: ContextVar[str | None] = ContextVar("client_ip", default=None)
