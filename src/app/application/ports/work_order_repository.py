"""Puerto (interfaz) del repositorio de órdenes de trabajo.

Define el contrato que deben implementar los adaptadores de infraestructura
para la persistencia de órdenes de trabajo.
"""

from typing import Protocol

from app.domain.entities import WorkOrder
from app.domain.value_objects import AssetId, CompanyId, WorkOrderId


class WorkOrderRepositoryPort(Protocol):
    """Puerto del repositorio de órdenes de trabajo.

    Define las operaciones de persistencia necesarias para gestionar
    órdenes de trabajo en el sistema.
    """

    async def save(self, work_order: WorkOrder) -> None:
        """Guarda una orden de trabajo (crea o actualiza)."""

    async def get_by_id(self, id: WorkOrderId, empresa_id: CompanyId) -> WorkOrder | None:
        """Obtiene una orden de trabajo por su ID dentro de una empresa."""

    async def get_by_code(self, codigo_ot: str, empresa_id: CompanyId) -> WorkOrder | None:
        """Obtiene una orden de trabajo por su código dentro de una empresa."""

    async def list_by_company(
        self,
        empresa_id: CompanyId,
        estado: str | None = None,
        activo_id: AssetId | None = None,
        tipo: str | None = None,
        supervisor_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[WorkOrder], int]:
        """Lista órdenes de trabajo de una empresa, con filtros opcionales."""

    async def get_by_report_id(
        self, reporte_id: str, empresa_id: CompanyId
    ) -> WorkOrder | None:
        """Obtiene una orden de trabajo asociada a un reporte de falla."""

    async def delete(self, id: WorkOrderId, empresa_id: CompanyId) -> None:
        """Elimina una orden de trabajo por su ID dentro de una empresa."""
