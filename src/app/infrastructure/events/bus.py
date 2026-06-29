"""Bus de eventos en proceso para el despacho síncrono de eventos de dominio."""

from collections.abc import Sequence

import structlog

from app.application.ports.event_bus import EventBusPort, EventHandler
from app.domain.events import DomainEvent

logger = structlog.get_logger()


class InProcessEventBus(EventBusPort):
    """Bus de eventos en proceso con registro de manejadores y envío síncrono.

    Los eventos sin manejadores registrados se descartan silenciosamente
    (solo se registra un log informativo). Esto es un diseño intencional:
    el bus no debe fallar si un evento no tiene consumidores.

    Attributes:
        published_count: Número de eventos publicados con éxito.
        failed_count: Número de eventos cuyos manejadores fallaron.
    """

    def __init__(self) -> None:
        """Inicializa el bus de eventos con diccionario de manejadores vacío."""
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}
        self.published_count = 0
        self.failed_count = 0

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        """Registra un manejador para un tipo de evento específico.

        Args:
            event_type: Clase del evento al que suscribirse.
            handler: Función asíncrona a ejecutar cuando ocurra el evento.
        """
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        """Despacha cada evento a los manejadores registrados para su tipo.

        Args:
            events: Secuencia de eventos de dominio a publicar.
        """
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
                    from app.domain.exceptions.base import DomainException
                    if isinstance(e, DomainException):
                        raise
                    self.failed_count += 1
                    logger.error(
                        "Manejador falló",
                        event_type=type(event).__name__,
                        event_id=str(event.event_id),
                        error=str(e),
                    )
