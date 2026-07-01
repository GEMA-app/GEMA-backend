"""Schemas JSON:API para el módulo de órdenes de trabajo.

Define los modelos de Pydantic para la validación y serialización
de las solicitudes y respuestas de la API de órdenes de trabajo,
siguiendo la especificación JSON:API (application/vnd.api+json).
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class WorkOrderAttributes(BaseModel):
    """Atributos de una orden de trabajo en una respuesta JSON:API."""

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


class WorkOrderResource(BaseModel):
    """Recurso JSON:API que encapsula los atributos de una orden."""

    type: str = Field(default="work_orders")
    id: str
    attributes: WorkOrderAttributes
    links: LinksObject | None = None


class WorkOrderDocument(BaseModel):
    """Documento JSON:API con un único recurso de orden de trabajo."""

    data: WorkOrderResource
    links: LinksObject | None = None
    meta: dict[str, object] | None = None


class WorkOrderListDocument(BaseModel):
    """Documento JSON:API con una lista de recursos de órdenes de trabajo."""

    data: list[WorkOrderResource]
    links: LinksObject | None = None
    meta: dict[str, object] | None = None


class CreateWorkOrderAttributes(BaseModel):
    """Atributos para crear una nueva orden de trabajo."""

    activo_id: str
    tipo: str
    codigo_ot: str | None = None
    supervisor_id: str | None = None
    descripcion_trabajo: str | None = None
    costo_estimado: float | None = None
    moneda: str = "USD"


class CreateWorkOrderResource(BaseModel):
    """Recurso JSON:API para crear una orden de trabajo."""

    type: str = Field(default="work_orders")
    attributes: CreateWorkOrderAttributes


class CreateWorkOrderRequest(BaseModel):
    """Cuerpo completo de la solicitud de creación (envelop JSON:API)."""

    data: CreateWorkOrderResource


class UpdateWorkOrderAttributes(BaseModel):
    """Atributos para actualizar una orden de trabajo (todos opcionales)."""

    descripcion_trabajo: str | None = None
    costo_estimado: float | None = None
    costo_real: float | None = None
    supervisor_id: str | None = None


class UpdateWorkOrderResource(BaseModel):
    """Recurso JSON:API para actualizar una orden de trabajo."""

    type: str = Field(default="work_orders")
    attributes: UpdateWorkOrderAttributes


class UpdateWorkOrderRequest(BaseModel):
    """Cuerpo completo de la solicitud de actualización (envelop JSON:API)."""

    data: UpdateWorkOrderResource


class ChangeStatusAttributes(BaseModel):
    """Atributos para cambiar el estado de una orden de trabajo."""

    estado: str
    motivo: str | None = None
    usuario_id: str | None = None


class ChangeStatusResource(BaseModel):
    """Recurso JSON:API para cambiar el estado de una orden."""

    type: str = Field(default="work_orders")
    attributes: ChangeStatusAttributes


class ChangeStatusRequest(BaseModel):
    """Cuerpo completo de la solicitud de cambio de estado (envelop JSON:API)."""

    data: ChangeStatusResource


class AssignTechnicianAttributes(BaseModel):
    """Atributos para asignar un técnico a una orden de trabajo."""

    tecnico_id: str


class AssignTechnicianResource(BaseModel):
    """Recurso JSON:API para asignar un técnico."""

    type: str = Field(default="work_order_technician")
    attributes: AssignTechnicianAttributes


class AssignTechnicianRequest(BaseModel):
    """Cuerpo completo de la solicitud de asignación de técnico."""

    data: AssignTechnicianResource


class WorkOrderStatusLogAttributes(BaseModel):
    """Atributos de una entrada del historial de estados."""

    ordenes_trabajo_id: str
    estado_anterior: str | None = None
    estado_nuevo: str
    usuario_id: str | None = None
    motivo: str | None = None
    fecha_cambio: datetime


class WorkOrderStatusLogResource(BaseModel):
    """Recurso JSON:API para una entrada de historial de estados."""

    type: str = Field(default="logs_estados_ordenes_trabajo")
    id: str
    attributes: WorkOrderStatusLogAttributes


class WorkOrderStatusLogListDocument(BaseModel):
    """Documento JSON:API con la lista de entradas de historial."""

    data: list[WorkOrderStatusLogResource]
