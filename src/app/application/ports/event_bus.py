from collections.abc import Sequence
from typing import Protocol

from app.domain.events import DomainEvent


class EventBusPort(Protocol):
    """Puerto para el bus de eventos de dominio."""

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        """Publica una secuencia de eventos de dominio."""
        ...
