"""Entidad de dominio para Intervención Técnica."""

from dataclasses import dataclass, replace
from datetime import datetime

from app.domain.enums import EstadoIntervencion
from app.domain.value_objects.identifier import IntervencionId, OrdenTrabajoId, UserId


@dataclass(frozen=True)
class IntervencionTecnica:
    """Intervención técnica realizada dentro de una orden de trabajo."""

    id: IntervencionId
    orden_trabajo_id: OrdenTrabajoId
    tecnico_id: UserId
    descripcion: str
    fecha_inicio: datetime
    fecha_fin: datetime | None
    horas_trabajadas: float
    costo: float
    estado: EstadoIntervencion
    observaciones: str | None

    def __post_init__(self) -> None:
        """Valida las invariantes de la entidad."""
        if self.horas_trabajadas < 0:
            raise ValueError("horas_trabajadas no puede ser negativo")
        if self.costo < 0:
            raise ValueError("costo no puede ser negativo")
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")

    @classmethod
    def crear(
        cls,
        orden_trabajo_id: OrdenTrabajoId,
        tecnico_id: UserId,
        descripcion: str,
        fecha_inicio: datetime,
        horas_trabajadas: float,
        costo: float,
        observaciones: str | None = None,
    ) -> "IntervencionTecnica":
        """Crea una nueva intervención técnica con estado inicial 'PENDIENTE'."""
        return cls(
            id=IntervencionId.generar(),
            orden_trabajo_id=orden_trabajo_id,
            tecnico_id=tecnico_id,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=None,
            horas_trabajadas=horas_trabajadas,
            costo=costo,
            estado=EstadoIntervencion.PENDIENTE,
            observaciones=observaciones,
        )

    def iniciar(self) -> "IntervencionTecnica":
        """Cambia el estado a 'EN_PROGRESO'."""
        if self.estado != EstadoIntervencion.PENDIENTE:
            raise ValueError("Solo se puede iniciar una intervención pendiente")
        return replace(self, estado=EstadoIntervencion.EN_PROGRESO)

    def completar(self, fecha_fin: datetime) -> "IntervencionTecnica":
        """Completa la intervención."""
        if self.estado != EstadoIntervencion.EN_PROGRESO:
            raise ValueError("Solo se puede completar una intervención en progreso")
        return replace(
            self,
            estado=EstadoIntervencion.COMPLETADA,
            fecha_fin=fecha_fin,
        )

    def cancelar(self) -> "IntervencionTecnica":
        """Cancela la intervención."""
        if self.estado == EstadoIntervencion.COMPLETADA:
            raise ValueError("No se puede cancelar una intervención ya completada")
        return replace(self, estado=EstadoIntervencion.CANCELADA)