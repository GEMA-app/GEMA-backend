from collections.abc import Sequence

import structlog

from app.application.ports.event_bus import EventBusPort
from app.domain.events import DomainEvent

logger = structlog.get_logger()


class LoggingEventBus(EventBusPort):
    """Implementación del puerto de bus de eventos que registra cada evento en los logs y mantiene métricas básicas."""

    def __init__(self) -> None:
        self.published_count = 0
        self.failed_count = 0

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            try:
                logger.info(
                    "Despachando evento de dominio",
                    event_type=event.__class__.__name__,
                    event_id=str(event.event_id),
                    occurred_on=event.occurred_on.isoformat(),
                    details={k: str(v) for k, v in event.__dict__.items() if k not in ("event_id", "occurred_on")},
                )
                self.published_count += 1
            except Exception as e:
                self.failed_count += 1
                logger.error(
                    "Error al despachar evento de dominio",
                    event_type=event.__class__.__name__,
                    event_id=str(event.event_id),
                    error=str(e),
                )
                # NO re-lanzar: el commit ya ocurrió exitosamente en BD
