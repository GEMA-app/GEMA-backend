"""Entidad FailureReport — reporte de falla de un activo con seguimiento de estado y prioridad."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums import PriorityLevel, ReportStatus
from app.domain.events import DomainEvent, EventProducer, FailureReportCreated
from app.domain.exceptions import (
    EmptyDescriptionError,
    EmptyLocationError,
    EmptyReportedByError,
    EmptyTitleError,
)
from app.domain.value_objects import CompanyId, FailureReportId


@dataclass
class FailureReport(EventProducer):
    """Entidad con comportamiento (Rich Entity) que representa un reporte de falla."""

    id: FailureReportId
    empresa_id: CompanyId
    title: str
    description: str
    location: str
    priority: PriorityLevel
    reported_by: str
    status: ReportStatus
    version: int = 1
    created_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia la lista de eventos acumulados.

        Returns:
            La lista de eventos de dominio acumulados, vaciando la lista interna.
        """
        events = self._events.copy()
        self._events.clear()
        return events

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        title: str,
        description: str,
        location: str,
        priority: PriorityLevel,
        reported_by: str,
    ) -> "FailureReport":
        """Crea un nuevo reporte de falla y emite FailureReportCreated.

        Args:
            empresa_id: Identificador de la empresa donde ocurre la falla.
            title: Título descriptivo del reporte.
            description: Descripción detallada de la falla.
            location: Ubicación donde se presenta la falla.
            priority: Nivel de prioridad del reporte.
            reported_by: Nombre o identificación de quien reporta.

        Returns:
            El nuevo reporte creado con el evento FailureReportCreated emitido.

        Raises:
            EmptyTitleError: Si el título está vacío.
            EmptyDescriptionError: Si la descripción está vacía.
            EmptyLocationError: Si la ubicación está vacía.
            EmptyReportedByError: Si el reportante está vacío.
        """
        if not title or not title.strip():
            raise EmptyTitleError("El título del reporte no puede estar vacío.")
        if not description or not description.strip():
            raise EmptyDescriptionError("La descripción del reporte no puede estar vacía.")
        if not location or not location.strip():
            raise EmptyLocationError("La ubicación del reporte no puede estar vacía.")
        if not reported_by or not reported_by.strip():
            raise EmptyReportedByError("El reportante no puede estar vacío.")

        report = cls(
            id=FailureReportId(uuid.uuid4()),
            empresa_id=empresa_id,
            title=title.strip(),
            description=description.strip(),
            location=location.strip(),
            priority=priority,
            reported_by=reported_by.strip(),
            status=ReportStatus.PENDING,
            version=1,
            created_at=datetime.now(UTC),
        )
        report._events.append(
            FailureReportCreated(
                failure_report_id=str(report.id),
                empresa_id=str(empresa_id),
                title=report.title,
            )
        )
        return report
