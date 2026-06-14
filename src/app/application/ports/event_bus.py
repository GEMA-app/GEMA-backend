from collections.abc import Awaitable, Callable, Sequence
from typing import Protocol

from app.domain.events import DomainEvent

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBusPort(Protocol):
    """Puerto para el bus de eventos de dominio."""

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        """Publica una secuencia de eventos de dominio."""
        ...

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Registra un handler para un tipo de evento."""
        ...
