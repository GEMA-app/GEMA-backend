from collections.abc import Sequence

import structlog

from app.application.ports.event_bus import EventBusPort, EventHandler
from app.domain.events import DomainEvent

logger = structlog.get_logger()


class InProcessEventBus(EventBusPort):
    """Bus de eventos en proceso con registro de handlers y dispatch síncrono."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}
        self.published_count = 0
        self.failed_count = 0

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Registra un handler para un tipo de evento."""
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        """Despacha cada evento a los handlers registrados para su tipo."""
        for event in events:
            logger.info(
                "Despachando evento de dominio",
                event_type=event.__class__.__name__,
                event_id=str(event.event_id),
            )
            self.published_count += 1
            for handler in self._handlers.get(type(event), []):
                try:
                    await handler(event)
                except Exception as e:
                    self.failed_count += 1
                    logger.error(
                        "Handler falló",
                        event_type=type(event).__name__,
                        event_id=str(event.event_id),
                        error=str(e),
                    )
