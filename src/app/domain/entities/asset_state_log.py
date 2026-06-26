"""Entidad AssetStateLog — registro auditable de cambio de estado de un activo."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import AssetStatus
from app.domain.events import DomainEvent, EventProducer
from app.domain.value_objects.identifier import AssetId, CompanyId


@dataclass
class AssetStateLog(EventProducer):
    """Entidad que representa un cambio de estado en el historial del activo.

    Registra la transición de estado_anterior a estado_nuevo, la fecha
    del cambio y el usuario responsable.
    """

    id: uuid.UUID
    empresa_id: CompanyId
    activo_id: AssetId
    estado_anterior: AssetStatus | None
    estado_nuevo: AssetStatus
    motivo: str | None
    fecha_cambio: datetime | None = None
    usuario_id: uuid.UUID | None = None
    version: int = 1
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia la lista de eventos acumulados.

        Returns:
            La lista de eventos de dominio acumulados, vaciando la lista interna.
        """
        events = self._events.copy()
        self._events.clear()
        return events
