"""DTOs del módulo PlanExecution."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class PlanExecutionCreateRequest:
    """DTO para la creación de una ejecución de plan."""

    plan_id: UUID
    work_order_id: UUID | None = None
    execution_date: datetime | None = None
    observations: str | None = None


@dataclass
class PlanExecutionResponse:
    """DTO de respuesta con datos de una ejecución de plan."""

    id: str
    empresa_id: str
    plan_id: str
    execution_date: datetime
    work_order_id: str | None = None
    observations: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class PlanExecutionListResponse:
    """DTO de respuesta con lista de ejecuciones de plan."""

    total: int = field(default_factory=lambda: 0)
    data: list[PlanExecutionResponse] = field(default_factory=list)
