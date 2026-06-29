"""DTOs (Data Transfer Objects) para el módulo de órdenes de trabajo.

Define las estructuras de datos inmutables que viajan entre las capas
de aplicación y presentación, incluyendo la respuesta estandarizada
y las solicitudes de creación, actualización y cambio de estado.
"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.entities import WorkOrder


@dataclass(frozen=True)
class WorkOrderResponse:
    """DTO de respuesta para una orden de trabajo.

    Contiene todos los campos de una orden serializados como strings
    y tipos planos, listo para ser convertido a JSON:API.
    """

    id: str
    company_id: str
    codigo_ot: str
    activo_id: str
    tipo: str
    estado: str
    reporte_id: str | None = None
    supervisor_id: str | None = None
    fecha_apertura: datetime | None = None
    fecha_inicio_trabajo: datetime | None = None
    fecha_cierre: datetime | None = None
    descripcion_trabajo: str | None = None
    costo_estimado: float | None = None
    costo_real: float | None = None
    moneda: str = "USD"
    validado_por_id: str | None = None
    fecha_validacion: datetime | None = None
    version: int = 1

    @classmethod
    def from_entity(cls, wo: WorkOrder) -> "WorkOrderResponse":
        """Construye un DTO de respuesta a partir de una entidad WorkOrder.

        Args:
            wo: Entidad WorkOrder de dominio.

        Returns:
            WorkOrderResponse: DTO con todos los campos serializados.
        """
        return cls(
            id=str(wo.id),
            company_id=str(wo.empresa_id),
            codigo_ot=wo.codigo_ot,
            activo_id=str(wo.activo_id),
            reporte_id=str(wo.reporte_id) if wo.reporte_id else None,
            tipo=wo.tipo.value,
            estado=wo.estado.value,
            supervisor_id=str(wo.supervisor_id) if wo.supervisor_id else None,
            fecha_apertura=wo.fecha_apertura,
            fecha_inicio_trabajo=wo.fecha_inicio_trabajo,
            fecha_cierre=wo.fecha_cierre,
            descripcion_trabajo=wo.descripcion_trabajo,
            costo_estimado=wo.costo_estimado,
            costo_real=wo.costo_real,
            moneda=wo.moneda,
            validado_por_id=str(wo.validado_por_id) if wo.validado_por_id else None,
            fecha_validacion=wo.fecha_validacion,
            version=wo.version,
        )


@dataclass(frozen=True)
class CreateWorkOrderRequest:
    """DTO de solicitud para crear una nueva orden de trabajo."""

    activo_id: str
    tipo: str
    codigo_ot: str | None = None
    supervisor_id: str | None = None
    descripcion_trabajo: str | None = None
    costo_estimado: float | None = None
    moneda: str = "USD"


@dataclass(frozen=True)
class UpdateWorkOrderRequest:
    """DTO de solicitud para actualizar una orden de trabajo existente.

    Todos los campos son opcionales; solo se actualizan los que se
    proporcionan (distintos de None).
    """
    descripcion_trabajo: str | None = None
    costo_estimado: float | None = None
    costo_real: float | None = None
    supervisor_id: str | None = None


@dataclass(frozen=True)
class ChangeWorkOrderStatusRequest:
    """DTO de solicitud para cambiar el estado de una orden de trabajo."""
    estado: str
    motivo: str | None = None
    usuario_id: str | None = None


@dataclass(frozen=True)
class WorkOrderStatusLogResponse:
    """DTO para representar una entrada del historial de estados de una OT."""
    id: str
    ordenes_trabajo_id: str
    estado_anterior: str | None
    estado_nuevo: str
    usuario_id: str | None
    motivo: str | None
    fecha_cambio: datetime
